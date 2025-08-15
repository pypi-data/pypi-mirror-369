from anndata import AnnData
from tqdm import tqdm
import pandas as pd
import numpy as np
from ._model import *
from ._utils import shuffling
from typing import Optional

class MoE_Runner(Runner):
    def __init__(
            self,
            adata: AnnData,
            choose_views: Optional[list] = None,
            expert_types: Optional[list] = None,
            out_dim: int = 30,
            device: str = 'cuda:0',
            verbose: bool = True
    ):
        super().__init__(adata, choose_views, None, None, device, verbose)
        
        # MoE特有参数
        self.expert_types = expert_types if expert_types else ['gcn'] * self.views
        self.out_dim = out_dim
        
        # 检查专家类型数量匹配
        if len(self.expert_types) != self.views:
            raise ValueError(f"expert_types length ({len(self.expert_types)}) must match views count ({self.views})")
            
        # 初始化MoE模型
        self.model = MoE_MVG(
            in_dims=self.in_feats,
            out_dim=self.out_dim,
            expert_types=self.expert_types
        ).to(self.device)
        
        if self.verbose:
            print("MoE Experts Configuration:")
            for i, (view, etype) in enumerate(zip(self.choose_views, self.expert_types)):
                print(f"View-{i}: {view} -> {etype.upper()} Expert")

    def fit(self, lr: Optional[float] = 0.01, epochs: Optional[int] = 100):
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        
        if self.verbose:
            print("-------Start MoE Training...")
        
        self.model.train()
        loss_all = []
        pbar = tqdm(range(epochs))
        
        for epoch in pbar:
            # 准备数据
            features = [g.ndata['feat'].to(self.device) for g in self.graph]
            edges = [g.edges()[0].to(self.device) for g in self.graph]  # 仅需要源节点索引
            
            # 前向传播
            optimizer.zero_grad()
            loss = self.model.total_loss(features, edges)
            
            # 反向传播
            loss.backward()
            optimizer.step()
            
            # 记录损失
            loss_all.append(loss.item())
            pbar.set_description(f'Epoch {epoch+1}/{epochs}')
            pbar.set_postfix(loss=f"{loss.item():.4f}")
        
        # 保存结果
        self.model.eval()
        with torch.no_grad():
            features = [g.ndata['feat'].to(self.device) for g in self.graph]
            edges = [g.edges()[0].to(self.device) for g in self.graph]
            z, gate_weights = self.model(features, edges)
            
        self.adata.uns['loss'] = loss_all
        self.adata.obsm['X_moe'] = z.cpu().numpy()
        self.adata.uns['gate_weights'] = gate_weights.cpu().numpy()
        
        if self.verbose:
            print("Training done.")
        
        return self.adata
        
class MoE_Runner_batch(Runner_batch):
    def __init__(
            self,
            adata: AnnData,
            choose_views: Optional[list] = None,
            expert_types: Optional[list] = None,
            out_dim: int = 30,
            device: str = 'cuda:0',
            verbose: bool = True
    ):
        super().__init__(adata, choose_views, None, None, device, verbose)
        
        # MoE特有参数
        self.expert_types = expert_types if expert_types else ['gcn'] * self.views
        self.out_dim = out_dim
        
        # 检查专家类型数量匹配
        if len(self.expert_types) != self.views:
            raise ValueError(f"expert_types length ({len(self.expert_types)}) must match views count ({self.views})")
            
        # 初始化MoE模型
        batch_size = len(self.adata.uns['batch_idx'][0])
        self.model = MoE_MVG(
            in_dims=self.in_feats,
            out_dim=self.out_dim,
            expert_types=self.expert_types
        ).to(self.device)
        
        if self.verbose:
            print("MoE Experts Configuration:")
            for i, (view, etype) in enumerate(zip(self.choose_views, self.expert_types)):
                print(f"View-{i}: {view} -> {etype.upper()} Expert")

    def fit(self, lr: Optional[float] = 0.01, epochs: Optional[int] = 100):
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        
        if self.verbose:
            print("-------Start MoE Batch Training...")
        
        self.model.train()
        loss_all = []
        pbar = tqdm(range(epochs))
        
        for epoch in pbar:
            batch_loss = 0
            for batch in self.dataloader:
                # 准备批次数据
                features = []
                edges = []
                for g in batch:
                    features.append(g.ndata['feat'].to(self.device))
                    edges.append(g.edges()[0].to(self.device))  # 仅需要源节点索引
                
                # 前向传播
                optimizer.zero_grad()
                loss = self.model.total_loss(features, edges)
                
                # 反向传播
                loss.backward()
                optimizer.step()
                
                batch_loss += loss.item()
            
            # 记录损失
            loss_all.append(batch_loss / len(self.dataloader))
            pbar.set_description(f'Epoch {epoch+1}/{epochs}')
            pbar.set_postfix(loss=f"{loss_all[-1]:.4f}")
        
        # 提取所有批次的嵌入
        self.model.eval()
        all_embeddings = []
        all_gate_weights = []
        
        with torch.no_grad():
            for batch in tqdm(self.dataloader, desc="Extracting embeddings"):
                features = []
                edges = []
                for g in batch:
                    features.append(g.ndata['feat'].to(self.device))
                    edges.append(g.edges()[0].to(self.device))
                
                z, gate_weights = self.model(features, edges)
                all_embeddings.append(z.cpu().numpy())
                all_gate_weights.append(gate_weights.cpu().numpy())
        
        # 合并并还原原始顺序
        final_emb, final_weights = self._reconstruct_embeddings(all_embeddings, all_gate_weights)
        
        # 保存结果
        self.adata.uns['loss'] = loss_all
        self.adata.obsm['X_moe'] = final_emb
        self.adata.uns['gate_weights'] = final_weights
        
        if self.verbose:
            print("Training done.")
        
        return self.adata

    def _reconstruct_embeddings(self, all_embeddings, all_gate_weights):
        """合并批次结果并还原原始细胞顺序"""
        # 合并所有批次的嵌入
        all_embeddings = np.concatenate(all_embeddings, axis=0)
        all_gate_weights = np.concatenate(all_gate_weights, axis=0)
        
        # 获取所有细胞索引（包括重复添加的）
        batch_idx = np.concatenate(self.adata.uns['batch_idx'])
        
        # 创建输出矩阵
        final_emb = np.zeros((self.adata.n_obs, all_embeddings.shape[1]))
        final_weights = np.zeros((self.adata.n_obs, all_gate_weights.shape[1]))
        
        # 保留每个细胞的第一次出现
        seen = set()
        for idx, cell in enumerate(batch_idx):
            if cell not in seen:
                final_emb[cell] = all_embeddings[idx]
                final_weights[cell] = all_gate_weights[idx]
                seen.add(cell)
        
        return final_emb, final_weights

# class Runner:
#     def __init__(
#             self,
#             adata: AnnData,
#             choose_views: Optional[list] = None,
#             hidden_size_v: Optional[list] = None,
#             hidden_size: Optional[list] = None,
#             device: str = 'cuda:0',
#             verbose: bool = True
#     ):
#         self.adata = adata
#         self.choose_views = choose_views
#         if self.choose_views is None:
#             self.choose_views = ['X_cn_norm', 'X_data', 'X_data_nbr']
#         else:
#             missing_views = [view for view in self.choose_views if view not in adata.obsm.keys()]
#             if missing_views:
#                 raise ValueError(f"The following views are missing in adata.obsm: {', '.join(missing_views)}")

#         self.views = len(self.choose_views)

#         self.graph_name = ['g_' + view for view in self.choose_views]
#         self.graph = [self.adata.uns[graph_name] for graph_name in self.graph_name]
#         self.adj = [g.ndata['adj'].to_dense() for g in self.graph]
#         self.mik = np.hstack((g.ndata['mik'] for g in self.graph))
#         self.edges = sum(g.number_of_edges() for g in self.graph)

#         self.feat = [g.ndata['feat'] for g in self.graph]
#         self.in_feats = [feat.shape[1] for feat in self.feat]

#         self.device = device
#         self.hidden_size_v = hidden_size_v
#         self.hidden_size = hidden_size
#         self.verbose = verbose

#         if self.hidden_size_v is None:
#             self.hidden_size_v = [10]

#         if self.hidden_size is None:
#             self.hidden_size = [32, 10]

#         if self.verbose:
#             print("-------Prepare training...")
#             print("Views: {}".format(self.views))
#             for i in range(len(self.choose_views)):
#                 print("View-{}: {}, DataSize: {} * {}; Graph Edges: {}".format(
#                     i,
#                     self.choose_views[i],
#                     self.feat[i].shape[0],
#                     self.feat[i].shape[1],
#                     self.graph[i].number_of_edges()
#                 ))
#             print("Mutual Information Matrix Size for training: {}".format(self.mik.shape))

#     def fit(self, lr: Optional[float] = 0.01, epochs: Optional[int] = 100, ):

#         # to device
#         self.feat = [feat.to(self.device) for feat in self.feat]
#         self.graph = [g.to(self.device) for g in self.graph]
#         self.adj = [adj.to(self.device) for adj in self.adj]

#         # model
#         self.model = MGAE(self.in_feats, self.hidden_size_v, self.hidden_size, self.views, self.adj[0].shape[0])
#         self.model_d = Discriminator(latent_dim=self.hidden_size[-1])
#         self.model = self.model.to(self.device)
#         self.model_d = self.model_d.to(self.device)

#         # optimizer
#         optim = torch.optim.Adam(self.model.parameters(), lr=lr)
#         # loss
#         pos_weight = torch.Tensor(
#             [float(self.graph[0].adjacency_matrix().to_dense().shape[0] ** 2 - self.edges / 2) / self.edges * 2]
#         )
#         criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight).to(self.device)
#         criterion_m = torch.nn.MSELoss().to(self.device)

#         if self.verbose:
#             print("-------Start training...")

#         self.model.train()
#         loss_all = []
#         pbar = tqdm(range(epochs))
#         for epoch in pbar:
#             adj_r, adj_logits, z = self.model.forward(self.graph, self.feat, self.device)
#             loss_gre = sum(criterion_m(adj_r, adj) for adj in self.adj) / self.views
#             loss_rec = sum(criterion(adj_logits[i], adj) for i, adj in enumerate(self.adj)) / self.views

#             loss_mim = 0
#             for i in range(self.mik.shape[1]):
#                 z_shuf = shuffling(z, latent=self.hidden_size[-1], device=self.device)
#                 z_comb = torch.cat((z, z_shuf), 1)
#                 z_shuf_scores = self.model_d(z_comb)
#                 z_idx = torch.cat((z, z[self.mik[:, i]]), 1)
#                 z_scores = self.model_d(z_idx)
#                 loss_mim += - torch.mean(
#                     torch.log(z_scores + 1e-6) + torch.log(1 - z_shuf_scores + 1e-6)
#                 )
#             loss = loss_gre + loss_rec + loss_mim
#             optim.zero_grad()
#             loss.backward()
#             optim.step()
#             pbar.set_description('Train Epoch: {}'.format(epoch + 1))
#             pbar.set_postfix(loss=f"{loss:.4f}")
#             loss_all.append(loss.data.cpu().numpy())

#         if self.verbose:
#             print("Training done.")

#         self.model.eval()
#         _, _, z = self.model.forward(self.graph, self.feat, self.device)

#         self.adata.uns['loss'] = loss_all
#         self.adata.obsm['X_scniche'] = z.data.cpu().numpy()
#         return self.adata


# class Runner_batch:
#     def __init__(
#             self,
#             adata: AnnData,
#             choose_views: Optional[list] = None,
#             hidden_size_v: Optional[list] = None,
#             hidden_size: Optional[list] = None,
#             device: str = 'cuda:0',
#             verbose: bool = True
#     ):
#         self.adata = adata
#         self.dataloader = self.adata.uns['dataloader']
#         self.choose_views = choose_views
#         if self.choose_views is None:
#             self.choose_views = ['X_cn_norm', 'X_data', 'X_data_nbr']
#         else:
#             missing_views = [view for view in self.choose_views if view not in adata.obsm.keys()]
#             if missing_views:
#                 raise ValueError(f"The following views are missing in adata.obsm: {', '.join(missing_views)}")

#         self.views = len(self.choose_views)

#         self.feat = [self.adata.obsm[view] for view in self.choose_views]
#         self.in_feats = [feat.shape[1] for feat in self.feat]

#         self.device = device
#         self.hidden_size_v = hidden_size_v
#         self.hidden_size = hidden_size
#         self.verbose = verbose

#         if self.hidden_size_v is None:
#             self.hidden_size_v = [10]

#         if self.hidden_size is None:
#             self.hidden_size = [32, 10]

#         if self.verbose:
#             print("-------Prepare training...")
#             print("Views: {}".format(self.views))
#             for i in range(len(self.choose_views)):
#                 print("View-{}: {}, DataSize: {} * {}".format(
#                     i,
#                     self.choose_views[i],
#                     self.feat[i].shape[0],
#                     self.feat[i].shape[1],
#                 ))
#             print("Batch size: {}".format(len(self.dataloader)))

#     def fit(self, lr: Optional[float] = 0.01, epochs: Optional[int] = 100, ):

#         # model
#         batch_size = len(self.adata.uns['batch_idx'][0])
#         self.model = MGAE(self.in_feats, self.hidden_size_v, self.hidden_size, self.views, batch_size)
#         self.model_d = Discriminator(latent_dim=self.hidden_size[-1])
#         self.model = self.model.to(self.device)
#         self.model_d = self.model_d.to(self.device)

#         # optimizer
#         optim = torch.optim.Adam(self.model.parameters(), lr=lr)

#         if self.verbose:
#             print("-------Start training...")

#         self.model.train()
#         loss_all = []
#         pbar = tqdm(range(epochs))
#         for epoch in pbar:
#             batch_loss = 0
#             for batch in self.dataloader:

#                 graphs = [batch[i] for i in range(len(batch))]
#                 feats = [g.ndata['feat'] for g in graphs]
#                 adjs = [g.ndata['adj'].to_dense() for g in graphs]
#                 mik = np.hstack((g.ndata['mik'] for g in graphs))
#                 edges = sum(g.number_of_edges() for g in graphs)

#                 # loss
#                 pos_weight = torch.Tensor(
#                     [float(graphs[0].adjacency_matrix().to_dense().shape[0] ** 2 - edges / 2) / edges * 2]
#                 )
#                 criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight).to(self.device)
#                 criterion_m = torch.nn.MSELoss().to(self.device)

#                 # to device
#                 feats = [feat.to(self.device) for feat in feats]
#                 graphs = [g.to(self.device) for g in graphs]
#                 adjs = [adj.to(self.device) for adj in adjs]

#                 adj_r, adj_logits, z = self.model.forward(graphs, feats, self.device)
#                 loss_gre = sum(criterion_m(adj_r, adj) for adj in adjs) / self.views
#                 loss_rec = sum(criterion(adj_logits[i], adj) for i, adj in enumerate(adjs)) / self.views

#                 loss_mim = 0
#                 for i in range(mik.shape[1]):
#                     z_shuf = shuffling(z, latent=self.hidden_size[-1], device=self.device)
#                     z_comb = torch.cat((z, z_shuf), 1)
#                     z_shuf_scores = self.model_d(z_comb)
#                     z_idx = torch.cat((z, z[mik[:, i]]), 1)
#                     z_scores = self.model_d(z_idx)
#                     loss_mim += - torch.mean(
#                         torch.log(z_scores + 1e-6) + torch.log(1 - z_shuf_scores + 1e-6)
#                     )

#                 loss = loss_gre + loss_rec + loss_mim
#                 optim.zero_grad()
#                 loss.backward()
#                 optim.step()

#                 batch_loss += loss.item()

#             loss_all.append(batch_loss)
#             pbar.set_description('Train Epoch: {}'.format(epoch))
#             pbar.set_postfix(loss=f"{batch_loss:.4f}")

#         if self.verbose:
#             print("Training done.")

#         self.model.eval()
#         emb = []
#         for batch in tqdm(self.dataloader):
#             graphs = [batch[i] for i in range(len(batch))]
#             feats = [g.ndata['feat'] for g in graphs]
#             graphs = [g.to(self.device) for g in graphs]
#             feats = [feat.to(self.device) for feat in feats]

#             _, _, z = self.model.forward(graphs, feats, self.device)
#             emb.append(list(z.data.cpu().numpy()))

#         emb = np.array(emb)
#         emb = pd.DataFrame(np.reshape(emb, (-1, emb.shape[2])))

#         idx = np.array(self.adata.uns['batch_idx']).flatten().tolist()
#         emb.index = idx
#         emb = emb[~emb.index.duplicated()]
#         emb.index = self.adata.obs_names[emb.index]
#         emb = emb.reindex(self.adata.obs_names)

#         self.adata.uns['loss'] = loss_all
#         self.adata.obsm['X_scniche'] = np.array(emb)
#         return self.adata
