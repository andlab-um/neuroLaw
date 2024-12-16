# Qi Yanyan Data 20240927
rm(list = ls())
setwd("/Users/yanyanqi/Library/CloudStorage/OneDrive-zzu.edu.cn/Involved Study/Neurolaw/plot/Behavior")
library(rstan)
library(tidyverse)
library(readxl)
library(ggthemes)

#----- life attitude -----
life <- read_excel("life_attitude.xlsx")
life_long <- life %>% 
  pivot_longer(lifeMisImmediate: lifeCapDelayed, names_to = "Group", values_to = "Life_Attitude") %>% 
  mutate(Criminal_scenario = case_when(str_detect(Group, "Mis") ~ "Misdemeanor",
                             str_detect(Group, "Fel") ~ "Felony",
                             str_detect(Group, "Cap") ~ "Capital"),
         `Time Delay` = if_else(str_detect(Group, "Delayed"), "Delayed","Immediate")) %>% 
  mutate(Criminal_scenario = factor(Criminal_scenario, levels = c("Misdemeanor", "Felony", "Capital")))

ggplot(life_long, aes(Criminal_scenario, Life_Attitude, fill = `Time Delay`)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.6) +
  geom_jitter(aes(color = `Time Delay`), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#045a8d", "#d95f0e")) +
  labs(x = "", y = "Life Attitude of TPP") +
  annotate("segment", x = 0.8, xend = 1.2, y = 9.2, yend = 9.2) +
  annotate("text", x = 1,y = 9.4, label = "**", size = 7) +
  annotate("segment", x = 1.8, xend = 2.2, y = 9.2, yend = 9.2) +
  annotate("text", x = 2,y = 9.4, label = "*", size = 7) +
  annotate("segment", x = 2.8, xend = 3.2, y = 9.2, yend = 9.2) +
  annotate("text", x = 3,y = 9.4, label = "**", size = 7) +
  annotate("segment", x = 1, xend = 3, y = 10.1, yend = 10.1) +
  annotate("text", x = 2,y = 10.3, label = "*", size = 7) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=17),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17))

#----- emotional arousal -----  
emotion <- read_excel("emotionalarousal_group.xlsx")
emotion_long <- emotion %>% 
  pivot_longer(emoMisImmediate:emoCapDelayed, names_to = "Group",values_to = "emotional_arousal") %>% 
  mutate(Criminal_scenario = case_when(str_detect(Group, "Mis") ~ "Mis",
                                       str_detect(Group, "Fel") ~ "Felony",
                                       str_detect(Group, "Cap") ~ "Capital"),
         `Time Delay` = if_else(str_detect(Group, "Delayed"), "Delayed","Immediate"))

# Mis
emo_mis <- emotion_long %>% 
  filter(Criminal_scenario == "Mis") 
  
ggplot(emo_mis,aes(group, emotional_arousal, fill = `Time Delay`)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.6) +
  geom_jitter(aes(color = `Time Delay`), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#045a8d", "#d95f0e")) +
  labs(x = "", y = "Emotional Arousal", title = "Misdemeanor") +
  annotate("segment", x = 0.8, xend = 1.2, y = 8.5, yend = 8.5) +
  annotate("text", x = 1,y = 8.7, label = "*", size = 7) +
  annotate("segment", x = 1, xend = 2, y = 9.3, yend = 9.3) +
  annotate("text", x = 1.5,y = 9.5, label = "**", size = 7) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=17),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17))

# Felony
emo_fel <- emotion_long %>% 
  filter(Criminal_scenario == "Felony") 

ggplot(emo_fel,aes(group, emotional_arousal, fill = `Time Delay`)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.6) +
  geom_jitter(aes(color = `Time Delay`), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#045a8d", "#d95f0e")) +
  labs(x = "",  y = '',title = "Felony") +
  annotate("segment", x = 1, xend = 2, y = 9.3, yend = 9.3) +
  annotate("text", x = 1.5,y = 9.5, label = "*", size = 7) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=17),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17))

# Capital
emo_cap <- emotion_long %>% 
  filter(Criminal_scenario == "Capital") 

  ggplot(emo_cap,aes(group, emotional_arousal, fill = `Time Delay`)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.6) +
  geom_jitter(aes(color = `Time Delay`), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#045a8d", "#d95f0e")) +
  labs(x = "",  y = '',title = "Capital offense") +
  scale_y_continuous(limits = c(0,9.5))+
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=17),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17))


p_emo <- cowplot::plot_grid(emo_mis+ theme(legend.position = 'none'), 
                   emo_fel+ theme(legend.position = 'none'), 
                   emo_cap, nrow = 1)

ggsave(p_emo, filename = "emo_arousal.pdf", width = 15, height = 3.3)


#----- punishment -----
punishment <- read_excel("punishment_group_time_case.xlsx")
pinishment_long <- punishment %>% 
  pivot_longer(lawMisImmediate:lawCapDelayed, names_to = "group", values_to = "Punishment") %>% 
  mutate(Criminal_scenario = case_when(str_detect(group, "Mis") ~ "Misdemeanor",
                                       str_detect(group, "Fel") ~ "Felony",
                                       str_detect(group, "Cap") ~ "Capital"),
         `Time Delay` = if_else(str_detect(group, "Delayed"), "Delayed","Immediate")) %>% 
  mutate(Criminal_scenario = factor(Criminal_scenario, levels = c("Misdemeanor", "Felony", "Capital")))

ggplot(pinishment_long, aes(Criminal_scenario, Punishment, fill = `Time Delay`)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.6) +
  geom_jitter(aes(color = `Time Delay`), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#045a8d", "#d95f0e")) +
  labs(x = "Criminal Scenario", y = "Punishment") +
  annotate("segment", x = 1, xend = 3, y = 10, yend = 10) +
  annotate("text", x = 2,y = 10.2, label = "*", size = 7) +
  annotate("segment", x = 1.8, xend = 2.2, y = 8.9, yend = 8.9) +
  annotate("text", x = 2,y = 9.1, label = "*", size = 7) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=17),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17))

punishment_noGro <- pinishment_long %>% 
  mutate(sub = rep(c(1:56), times = 1, each = 6) %>% as.factor()) %>% 
  group_by(Criminal_scenario, sub, `Time Delay`) %>% 
  summarise(Punishment = mean(Punishment)) %>% 
  ungroup()


ggplot(punishment_noGro, aes(Criminal_scenario, Punishment, fill = `Time Delay`)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.6) +
  geom_jitter(aes(color = `Time Delay`), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#045a8d", "#d95f0e")) +
  labs(x = "", y = "Punishment") +
  annotate("segment", x = 1, xend = 3, y = 9.5, yend = 9.5) +
  annotate("text", x = 2,y = 9.7, label = "*", size = 7) +
  annotate("segment", x = 1.8, xend = 2.2, y = 8, yend = 8) +
  annotate("text", x = 2,y = 8.2, label = "*", size = 7) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=17),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17))

#
punishment_noCri <- pinishment_long %>% 
  mutate(sub = rep(c(1:56), times = 1, each = 6) %>% as.factor()) %>% 
  group_by(Group, sub, `Time Delay`) %>% 
  summarise(Punishment = mean(Punishment)) %>% 
  ungroup()

ggplot(punishment_noCri, aes(Group, Punishment, fill = `Time Delay`)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.6) +
  geom_jitter(aes(color = `Time Delay`), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#045a8d", "#d95f0e")) +
  labs(x = "", y = "Punishment") +
  annotate("segment", x = 1, xend = 2, y = 8, yend = 8) +
  annotate("text", x = 1.5,y = 8.2, label = "**", size = 7) +
  annotate("segment", x = 1.8, xend = 2.2, y = 7, yend = 7) +
  annotate("text", x = 2,y = 7.2, label = "***", size = 7) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=17),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17))

# ----- brain -----
setwd("/Users/yanyanqi/Library/CloudStorage/OneDrive-zzu.edu.cn/Involved Study/Neurolaw/plot/ROI")
## ----right Caudate----
caudate <- read_excel("Time_Caudate.xlsx") %>% 
  mutate(Immediate = `CN-R_Immediate`,
         Delayed = `CN-R_Delayed`) %>% 
  pivot_longer(Immediate:Delayed, names_to = "Time Delay", values_to = "caudate")

p_caudate <- ggplot(caudate, aes(Group_ID, caudate, fill = `Time Delay`)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.6) +
  geom_jitter(aes(color = `Time Delay`), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#045a8d", "#d95f0e")) +
  annotate("segment", x = 0.8, xend = 1.2, y = 1.5, yend = 1.5) +
  annotate("text", x = 1,y = 1.6, label = "*", size = 9) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=19),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17)) +
  scale_x_discrete(labels = NULL) +
  labs(x = "", y = "Beta Value of Caudate")

ggsave(p_caudate, filename = "caudate.pdf", width = 5, height = 3.3)


## ----left dmPFC----
dmPFC <- read_excel("Time_dmPFC.xlsx") %>% 
  pivot_longer(`dmpfc-current`:dmpfc_delay, names_to = "group", values_to = "left_dmPFC") %>% 
  mutate(`Time Delay` = if_else(str_detect(group, "delay"), "Delayed","Immediate"))

p_dmPFC <- ggplot(dmPFC, aes(Group_ID, left_dmPFC, fill = `Time Delay`)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.6) +
  geom_jitter(aes(color = `Time Delay`), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#045a8d", "#d95f0e")) +
  annotate("segment", x = 0.8, xend = 1.2, y = 3, yend = 3) +
  annotate("text", x = 1,y = 3.1, label = "**", size = 9) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=19),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17)) +
  scale_x_discrete(labels = NULL) +
  labs(x = "", y = "Beta Value of dmPFC")

ggsave(p_dmPFC, filename = "dmPFC.pdf", width = 5, height = 3.3)


## ----right vmPFC----
vmPFC <- read_excel("Time_vmPFC.xlsx") %>% 
  pivot_longer(`VMPFC-R_Immediate`:`VMPFC-R_Delayed`, names_to = "group", values_to = "right_vmPFC") %>% 
  mutate(`Time Delay` = if_else(str_detect(group, "Delay"), "Delayed","Immediate"))

p_vmPFC <- ggplot(vmPFC, aes(Group_ID, right_vmPFC, fill = `Time Delay`)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.6) +
  geom_jitter(aes(color = `Time Delay`), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#045a8d", "#d95f0e")) +
  annotate("segment", x = 0.8, xend = 1.2, y = 1.5, yend = 1.5) +
  annotate("text", x = 1,y = 1.6, label = "*", size = 9) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=19),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17)) +
  scale_x_discrete(labels = NULL) +
  labs(x = "", y = "Beta Value of vmPFC")

ggsave(p_vmPFC, filename = "vmPFC.pdf", width = 5, height = 3.3)


## ----left vlPFC----
vlPFC <- read_excel("Time_vlPFC.xlsx") %>% 
  pivot_longer(`VLPFC-L_Immediate`:`VLPFC-L_Delayed`, names_to = "group", values_to = "left_vlPFC") %>% 
  mutate(`Time Delay` = if_else(str_detect(group, "Delay"), "Delayed","Immediate"))

p_vlPFC <- ggplot(vlPFC, aes(Group_ID, left_vlPFC, fill = `Time Delay`)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.6) +
  geom_jitter(aes(color = `Time Delay`), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#045a8d", "#d95f0e")) +
  annotate("segment", x = 0.8, xend = 1.2, y = 5, yend = 5) +
  annotate("text", x = 1,y = 5.1, label = "**", size = 9) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=19),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17)) +
  scale_x_discrete(labels = NULL) +
  labs(x = "", y = "Beta Value of vlPFC")

ggsave(p_vlPFC, filename = "vlPFC.pdf", width = 5, height = 3.3)


## ----left TPJ----
lTPJ <- read_excel("Time_lTPJ.xlsx") %>% 
  pivot_longer(`TPJ-L_Immediate`:`TPJ-L_Delayed`, names_to = "group", values_to = "left_TPJ") %>% 
  mutate(`Time Delay` = if_else(str_detect(group, "Delay"), "Delayed","Immediate"))

p_lTPJ <- ggplot(lTPJ, aes(Group_ID, left_TPJ, fill = `Time Delay`)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.6) +
  geom_jitter(aes(color = `Time Delay`), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#045a8d", "#d95f0e")) +
  annotate("segment", x = 0.8, xend = 1.2, y = 6.3, yend = 6.3) +
  annotate("text", x = 1,y = 6.4, label = "*", size = 9) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=19),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17)) +
  scale_x_discrete(labels = NULL) +
  labs(x = "", y = "Beta Value of TPJ")

ggsave(p_lTPJ, filename = "TPJ.pdf", width = 5, height = 3.3)

# ----- group effect -----
## ----precuneus----
precuneus <- read_excel("precuneus_group effect.xlsx") %>% 
  mutate(Group = Group_ID)

p_precuneus <- ggplot(precuneus, aes(Group, `beta value of precuneus`, fill = Group)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               # position = position_dodge(width = 0.4),
               width = 0.4) +
  geom_jitter(aes(color = Group), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#407870", "#755878")) +
  annotate("segment", x = 1, xend = 2, y = 2.5, yend = 2.5) +
  annotate("text", x = 1.5,y = 2.6, label = "*", size = 10) +
  theme_minimal() +
  theme(axis.text=element_text(size=18,color = 'black'),
        axis.title = element_text(size=20),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17)) +
  labs(x = "", y = "Beta Value of Precuneus")

ggsave(p_precuneus, filename = "precuneus.pdf", width = 5, height = 3.7)


## ----left TPJ group----
lTPJ_group <- read_excel("group_left TPJ.xlsx") %>% 
  mutate(Group = Group_ID)

p_lTPJ_group <- ggplot(lTPJ_group, aes(Group, `beta value of left TPJ`, fill = Group)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.4) +
  geom_jitter(aes(color = Group), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#407870", "#755878")) +
  annotate("segment", x = 1, xend = 2, y = 3, yend = 3) +
  annotate("text", x = 1.5,y = 3.1, label = "*", size = 10) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=19),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17)) +
  labs(x = "", y = "Beta Value of TPJ")

ggsave(p_lTPJ_group, filename = "lTPJ_group.pdf", width = 5, height = 3.7)


## ----LTPJ-lDLPFC FC----
FC <- read_excel("FC.xlsx") %>% 
  mutate(Group = Group_ID)

p_FC <- ggplot(FC, aes(Group, task_based_FC, fill = Group)) +
  stat_summary(geom = "col", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), width = 0.4) +
  geom_jitter(aes(color = Group), 
              position = position_jitterdodge(0.1),
              alpha = 0.3) +
  stat_summary(geom = "linerange", fun.data = "mean_se", 
               position = position_dodge(width = 0.7), alpha = 1) +
  scale_fill_manual(values=c("#cccccc", "#cccccc")) +
  scale_color_manual(values=c("#407870", "#755878")) +
  annotate("segment", x = 1, xend = 2, y = 1, yend = 1) +
  annotate("text", x = 1.5,y = 1.1, label = "*", size = 10) +
  theme_minimal() +
  theme(axis.text=element_text(size=17,color = 'black'),
        axis.title = element_text(size=19),
        legend.text = element_text(size=17,color = 'black'), 
        legend.title = element_text(size=17)) +
  labs(x = "", y = "lTPJ - DLPFC FC")

ggsave(p_FC, filename = "FC.pdf", width = 5, height = 3.7)













