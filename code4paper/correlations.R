# neurolaw 20241005
# brain-behavior correlation 
rm(list = ls())
library(readxl)
library(Hmisc)
library(grid)
library(ggplot2)

setwd("/Users/yanyanqi/Library/CloudStorage/OneDrive-zzu.edu.cn/Involved Study/Neurolaw/plot/behavior-brain")
# mis
Mis <- read_excel("punish_brain_Mis.xlsx")
Mis.spp <- subset(Mis, Group== 'SPP')
Mis.tpp <- subset(Mis, Group == 'TPP')

r.Mis <-  rcorr(as.matrix(Mis[,c(5,8,11,14,17,20)]),type="pearson")
print(r.Mis)

r.Mis.spp <-  rcorr(as.matrix(Mis.spp[,c(5,8,11,14,17,20)]),type="pearson")
print(r.Mis.spp)

r.Mis.tpp <-  rcorr(as.matrix(Mis.tpp[,c(5,8,11,14,17,20)]),type="pearson")
print(r.Mis.tpp)

# felony
felony <- read_excel("punish_brain_Felony.xlsx")
fel.spp <- subset(felony, Group== 'SPP')
fel.tpp <- subset(felony, Group == 'TPP')

r.fel <-  rcorr(as.matrix(felony[,c(4,7,10,13,16,19)]),type="pearson")
print(r.fel)

r.fel.spp <-  rcorr(as.matrix(fel.spp[,c(5,8,11,14,17,20)]),type="pearson")
print(r.fel.spp)

r.fel.tpp <-  rcorr(as.matrix(fel.tpp[,c(4,7,10,13,16,19)]),type="pearson")
print(r.fel.tpp)

# plot 
p_felony_TPJ <- ggplot(fel.spp, aes(x = FelDiff, y = Diff_lTPJ)) +
  geom_point(color = "#407870", size = 3, shape = 21, fill = "#407870", alpha = 0.4) +  
  geom_smooth(method = "lm", se = TRUE, color = "#0072B2", fill = "#A4C8E1", size = 2) +  
  labs(title = expression(paste("SPP-Felony (",italic("r"),"= -0.422, ", italic("p"), "= 0.032)")),
       x = "Degree of Punishment \n (Immediate-Delayed) ",
       y = "Betas \n (Immediate-Delayed)") +
  theme_minimal(base_size = 15) +  # 
  theme(
    plot.title = element_text(hjust = 0),  # 标题居中
    axis.text.x = element_text(angle = 0, hjust = 1),  # 旋转 x 轴标签
    legend.position = "top" )+
  theme(axis.text=element_text(size=16,color = 'black'),
        axis.title = element_text(size=18),
        legend.text = element_text(size=15,color = 'black'), 
        legend.title = element_text(size=15))

ggsave(p_felony_TPJ, filename = "Corr_TPJ.pdf", width = 5.5, height = 5)


    




# Capital offense
cap <- read_excel("punish_brain_Cap.xlsx")
cap.spp <- subset(cap, Group== 'SPP')
cap.tpp <- subset(cap, Group == 'TPP')

r.cap <-  rcorr(as.matrix(cap[,c(5,8,11,14,17,20)]),type="pearson")
print(r.cap)

r.cap.spp <-  rcorr(as.matrix(cap.spp[,c(5,8,11,14,17,20)]),type="pearson")
print(r.cap.spp)

r.cap.tpp <-  rcorr(as.matrix(cap.tpp[,c(5,8,11,14,17,20)]),type="pearson")
print(r.cap.tpp)





