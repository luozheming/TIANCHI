# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 10:37:13 2018

@author: 颜
"""

import torch

class Propagator(torch.nn.Module):
    def __init__(self,shape):
        super(Propagator,self).__init__()
        self.shape=shape
        self.float_type='torch.cuda.FloatTensor'
        self.int_type='torch.cuda.IntTensor'

    def forward(self,A,t):
        P_B=torch.ones([self.shape[0],self.shape[1],5]).type(self.float_type)
        direction_map=torch.Tensor([0,1,2,3,4]).type(self.int_type)
        direction_map=direction_map.view([1,1,5]).expand([self.shape[0],self.shape[1],5])
        P_A_local=A[:,:,0]
        p_B=A[:,:,1]
        for i in range(5):
            P_A=self.adjust(P_A_local,i)
            P_B[:,:,i]=1.-(1.-P_A)*(1.-p_B)
        P_B_reduce,direction_map=torch.min(P_B,2)
        #mask=(P_B<=P_B_reduce).type(self.int_type)
        #direction_map=torch.max(direction_map*mask,2)
        B_score=2*t*(1-P_B_reduce)+1440*P_B_reduce
        return P_B_reduce,direction_map,B_score

    def adjust(self,A,direction):
        if direction==0:
            B=A.clone()
        elif direction==1:
            B=A.clone()
            C=B[:,self.shape[1]-1].clone()
            B=torch.cat((B[:,1:self.shape[1]],C.view([self.shape[0],1])),1)
        elif direction==2:
            B=A.clone()
            C=B[:,0].clone()
            B=torch.cat((C.view([self.shape[0],1]),B[:,0:self.shape[1]-1]),1)
        elif direction==3:
            B=A.clone()
            C=B[self.shape[0]-1,:].clone()
            B=torch.cat((B[1:self.shape[0],:],C.view([1,self.shape[1]])),0)
        elif direction==4:
            B=A.clone()
            C=B[0,:].clone()
            B=torch.cat((C.view([1,self.shape[1]]),B[0:self.shape[0]-1,:]),0)
        return B
