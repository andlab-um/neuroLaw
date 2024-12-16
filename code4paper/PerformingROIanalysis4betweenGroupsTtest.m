clear all; close all;
% cd H:\Wuhan_schz
%% path
path.root='F:\Results';
path.data='F:\Results\firstLevel_neurolaw_concated_revised20221219';
path.roi='F:\Results\secondlevel\ROI_analysis\ROIs_threeNetworks';  % the directory storing nii files of the ROIs

%% matlab batch
% Initialize SPM




num.chars = 2; % # of characters to consider
subject = struct2cell(dir(path.data))'; % list folder content
subject = char(subject(:, 1)); % convert to string
subject(subject(:, 1) == '.', :) = []; % find hidden folders/files (starting with '.') and delete
num.subjects = size(subject, 1); % # of subjects
subject = cellstr(subject); % make cell array (for convenience)

% subject_2nd_part=subject([1:27,29:37,40:59],1);

subject_2nd_part=subject([1:23,57:59],1);
subject_3rd_part=subject([24:27,29:37,40:56],1); % delete 38,48,49
% subject_2nd_part=subject([1:23,57:59],1);
% subject_3rd_part=subject(24:56,1);

parties={'2nd','3rd'};

%% load ROIs
ROIs=spm_select('List',path.roi,'.nii');
ROIs=cellstr(ROIs);     
% ROIs=ROIs([10:18,1:9]);
ROIs_array=cell(length(ROIs),1);
ROI_names=cell(length(ROIs),1);
for ii=1:length(ROIs)
     temp_v=spm_vol(fullfile(path.roi,ROIs{ii}));
    temp_IM=spm_read_vols(temp_v);
    ROIs_array{ii}=temp_IM;
    temp_name=ROIs{ii};
    temp_name(1:2)=[];
%     temp_name=strrep(temp_name,[num2str(ii) '_'],'');
    temp_name=strrep(temp_name,'.nii','');
    temp_name=strrep(temp_name,'_','-');
    ROI_names{ii}=temp_name;
end

% contrast_set={'current','delay','current-delay','cat1','cat2','cat3'};
contrast_set={'current','delay','current-delay','cat1','cat2','cat3','cat3-cat2','cat3-cat1','del_cat1-cur_cat1','del_cat2-cur_cat2',...
               'del_cat3-cur_cat3','cur_cat3-cur_cat2','car_cat3-cur_cat1','del_cat3-del_cat2','del_cat3-del_cat1'};
           
workdir=fullfile(path.root,'secondlevel','ROI_analysis','betweenGroup_ttest2_ROIanalysis_202304'); %% output directory
if ~exist(workdir,'dir')
mkdir(workdir);
end

pValue_ID_fdr=zeros(15,1);
pvalue_status=zeros(15,1);
for ck=1:15%:length(parties)

%% ROI

% workdir=fullfile(path.root,'secondlevel',[parties{k} '_party_neuroLaw_anowa_category_56Subj']);


%%

for k=1:2
temp_subj.(['S' parties{k}])=eval(['subject_' parties{k} '_part']);
% Image.(['S' parties{k}])=cell(length(temp_subj.(['S' parties{k}])),1);

contrst.(['S' parties{k} '_c' num2str(ck)])=zeros(length(temp_subj.(['S' parties{k}])),length(ROIs_array));

for i=1:length(temp_subj.(['S' parties{k}]))
   
    if ck<10
%     Image.(['S' parties{k}]){i}=fullfile(path.data,temp_subj.(['S' parties{k}]){i},['con_000' num2str(ck) '.nii']);
     temp_v=spm_vol(fullfile(path.data,temp_subj.(['S' parties{k}]){i},['con_000' num2str(ck) '.nii']));
     temp_image=spm_read_vols(temp_v);
    else
%      Image.(['S' parties{k}]){i}=fullfile(path.data,temp_subj.(['S' parties{k}]){i},['con_00' num2str(ck) '.nii']); 
    temp_v=spm_vol(fullfile(path.data,temp_subj.(['S' parties{k}]){i},['con_00' num2str(ck) '.nii']));
     temp_image=spm_read_vols(temp_v);
    end
    
    for roi_ord=1:length(ROIs_array)
        temp_mean_sig=temp_image(ROIs_array{roi_ord}>0.3);
        temp_mean_sig(isnan(temp_mean_sig))=[];
      contrst.(['S' parties{k} '_c' num2str(ck)])(i,roi_ord)=mean(temp_mean_sig,'all');
    end

end
end

% perform t test
ttest_results.(['c' num2str(ck)])=zeros(length(ROIs_array),1);
ttest_stats.(['c' num2str(ck)])=zeros(length(ROIs_array),3);

for roi_ord2=1:length(ROIs_array)
    [~,temp_p,~,temp_stats]=ttest2(contrst.(['S' parties{1} '_c' num2str(ck)])(:,roi_ord2), contrst.(['S' parties{2} '_c' num2str(ck)])(:,roi_ord2));
    ttest_results.(['c' num2str(ck)])(roi_ord2)=temp_p;
       ttest_stats.(['c' num2str(ck)])(roi_ord2,1)=temp_stats.tstat;
    ttest_stats.(['c' num2str(ck)])(roi_ord2,2)=temp_stats.df;
    ttest_stats.(['c' num2str(ck)])(roi_ord2,3)=temp_stats.sd;
    
end

%% FDR correction
for_fdr_pvalue=ttest_results.(['c' num2str(ck)]);
[temp_pID,temp_pN]=gretna_FDR(for_fdr_pvalue,0.05);
aft_fdr_corrected_status=zeros(length(ttest_results.(['c' num2str(ck)])),1);
if ~isempty(temp_pID)
    pValue_ID_fdr(ck)=temp_pID;
    temp_fdr_status=for_fdr_pvalue<=temp_pID;
    aft_fdr_corrected_status=double(temp_fdr_status);
end

mean_2nd=mean(contrst.(['S' parties{1} '_c' num2str(ck)]),1);
mean_3rd=mean(contrst.(['S' parties{2} '_c' num2str(ck)]),1);
forplot_data=[mean_2nd',mean_3rd'];
figure(ck);
b=bar(forplot_data);
hold on;

xtips2 = b(2).XEndPoints;
xtips1 = b(1).XEndPoints;

ytips1=b(1).YEndPoints;
ytips2=b(2).YEndPoints;
ytips=zeros(size(ytips1));

    for yOrd=1:length(ytips1)
%         if ytips1(yOrd)>ytips2(yOrd)
%             ytips(yOrd)=ytips1(yOrd)+0.03;
%         else
%             ytips(yOrd)=ytips2(yOrd)+0.03;
%         end
         if ytips1(yOrd)>=ytips2(yOrd) && ytips1(yOrd)>0
            ytips(yOrd)=ytips1(yOrd)+0.03;
        elseif ytips1(yOrd)<ytips2(yOrd) && ytips2(yOrd)>0
            ytips(yOrd)=ytips2(yOrd)+0.03;
        elseif ytips1(yOrd)>=ytips2(yOrd) && ytips2(yOrd)<=0
            ytips(yOrd)=ytips2(yOrd)-0.03;
        elseif ytips1(yOrd)<ytips2(yOrd) && ytips1(yOrd)<=0
            ytips(yOrd)=ytips1(yOrd)-0.03;
         end
         %% label position
        if  ytips(yOrd)>0
            label_pos=ytips(yOrd)+0.03;
        else
          label_pos=ytips(yOrd)-0.03;  
        end
      
        if ttest_results.(['c' num2str(ck)])(yOrd)<0.05 && aft_fdr_corrected_status(yOrd)==1
            plot([xtips1(yOrd),xtips2(yOrd)],[ytips(yOrd),ytips(yOrd)],'r-');
%             scatter((xtips1(yOrd)+xtips2(yOrd))/2,ytips(yOrd)+0.03,'*');
             text((xtips1(yOrd)+xtips2(yOrd))/2,label_pos,'**','FontSize',14);
        elseif ttest_results.(['c' num2str(ck)])(yOrd)<0.05 && aft_fdr_corrected_status(yOrd)==0
            plot([xtips1(yOrd),xtips2(yOrd)],[ytips(yOrd),ytips(yOrd)],'r-');
%             scatter((xtips1(yOrd)+xtips2(yOrd))/2,ytips(yOrd)+0.03,'*');
             text((xtips1(yOrd)+xtips2(yOrd))/2,label_pos,'*','FontSize',14);
        end
        
    end
    xticks(1:18);
    xticklabels(ROI_names);
    xtickangle(45);
    hold off;
 saveas(ck,fullfile(workdir,[contrast_set{ck} '.png']),'png');

% if there are significant contrasts
  if any(ttest_results.(['c' num2str(ck)])<0.05)
      pvalue_status(ck)=1;
  end
end
output.pValue_ID_fdr=pValue_ID_fdr;
output.tstat_df_sd= ttest_stats;
output.contrst_value=contrst;
output.contrast_name=contrast_set;
output.ttest2_pvalue=ttest_results;
output.pvalue_status=pvalue_status;
% save(fullfile(workdir,'output_values.mat'),'output');
save(fullfile(workdir,'output_values_withStats.mat'),'output');