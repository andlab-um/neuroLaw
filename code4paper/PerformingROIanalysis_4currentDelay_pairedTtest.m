clear all; close all;
% cd H:\Wuhan_schz
%% path
% path.root='F:\Results';
% path.data='F:\Results\firstLevel_neurolaw_concated';

path.root='Z:\experiment_data\jiamin_neurolaw\Results';
path.data='Z:\experiment_data\jiamin_neurolaw\Results\firstLevel_neurolaw_concated_divide_Time_cat';
path.data2='Z:\experiment_data\jiamin_neurolaw\Results\firstLevel_neurolaw_concated_revised20221219';
path.roi='Z:\experiment_data\jiamin_neurolaw\myroi6';  %% ROI directory, please note, the resolution of the ROI files shoud match with the image files of the contrast 
%% matlab batch
% Initialize SPM




num.chars = 2; % # of characters to consider
subject = struct2cell(dir(path.data))'; % list folder content
subject = char(subject(:, 1)); % convert to string
subject(subject(:, 1) == '.', :) = []; % find hidden folders/files (starting with '.') and delete
num.subjects = size(subject, 1); % # of subjects
subject = cellstr(subject); % make cell array (for convenience)

% subject_2nd_part=subject([1:27,29:37,40:59],1);


%     subject_2nd_part=subject([1:23,57:59],1);
% subject_3rd_part=subject(24:56,1);
subject_2nd_part=subject([1:23,57:59],1);
subject_3rd_part=subject([24:27,29:37,40:56],1);
subject_all_part=subject([1:27,29:37,40:59],1);
parties={'2nd','3rd','all'};

CondNames={'overall','cat1','cat2','cat3'};


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

workdir=fullfile(path.root,'secondlevel','ROI_analysis','CurrentDelay_pairedT_ROIanalysis_202304');  %% the directory to save the output
if ~exist(workdir,'dir')
mkdir(workdir);
end

pvalue_status=zeros(4,3);
n=0;
for k=1:length(parties)
    
   
  for ConOrd=1:4
%% ROI
%roi=[path.roi,filesep,'comp_' num2str(i) '.img'];
%outdir=[path.output,filesep,'ROI' num2str(i)];
% workdir=fullfile(path.root,'secondlevel',[parties{k} '_party_neuroLaw_pairedT_current_delayed_56Subjs']);
% workdir=fullfile(path.root,'secondlevel','neuroLaw_pairedT_current_delayed_56Subjs_20221220',parties{k},CondNames{ConOrd});
% if ~exist(workdir,'dir')
% mkdir(workdir);
% end
%output.name=['ROI_' num2str(i)];
% statImages=spm_select('FPListRec',fullfile(path.firstLevel,stats_set{i}),'con_0002.nii');
% statImages=cellstr(statImages);


%%
 
temp_subj.(['S' parties{k}])=eval(['subject_' parties{k} '_part']);
contrst.(['S' parties{k} '_c' num2str(ConOrd) '_Tcurr'])=zeros(length(temp_subj.(['S' parties{k}])),length(ROIs_array));
contrst.(['S' parties{k} '_c' num2str(ConOrd) '_Tdelay'])=zeros(length(temp_subj.(['S' parties{k}])),length(ROIs_array));
for i=1:length(temp_subj.(['S' parties{k}]))
    tempImage=cell(2,1);
    if ConOrd==1
    tempImage{1}=fullfile(path.data2,temp_subj.(['S' parties{k}]){i},'con_0001.nii');
    tempImage{2}=fullfile(path.data2,temp_subj.(['S' parties{k}]){i},'con_0002.nii');
    else
     tempImage{1}=fullfile(path.data,temp_subj.(['S' parties{k}]){i},['con_000' num2str(ConOrd-1) '.nii']);
    tempImage{2}=fullfile(path.data,temp_subj.(['S' parties{k}]){i},['con_000' num2str(ConOrd-1+3) '.nii']);   
    end
    
    % load contrast image: current
     temp_v1=spm_vol(tempImage{1});
     temp_image1=spm_read_vols(temp_v1);
     % load contrast image: delay
      temp_v2=spm_vol(tempImage{2});
     temp_image2=spm_read_vols(temp_v2);
     
       for roi_ord=1:length(ROIs_array)
           %image 1
        temp_mean_sig1=temp_image1(ROIs_array{roi_ord}>0.3);
        temp_mean_sig1(isnan(temp_mean_sig1))=[];
      contrst.(['S' parties{k} '_c' num2str(ConOrd) '_Tcurr'])(i,roi_ord)=mean(temp_mean_sig1,'all','omitnan');
           %image 2
        temp_mean_sig2=temp_image2(ROIs_array{roi_ord}>0.3);
        temp_mean_sig2(isnan(temp_mean_sig2))=[];
      contrst.(['S' parties{k} '_c' num2str(ConOrd) '_Tdelay'])(i,roi_ord)=mean(temp_mean_sig2,'all','omitnan');
      
      
      end
     
    
    
end
% contrast weights
% weights_con=repmat([1/length(subject) -1/length(subject)],1,length(subject));
% perform t test
ttest_results.(['S' parties{k} '_c' num2str(ConOrd)])=zeros(length(ROIs_array),1);
ttest_stats.(['S' parties{k} '_c' num2str(ConOrd)])=zeros(length(ROIs_array),3);

for roi_ord2=1:length(ROIs_array)
    [~,temp_p,~,temp_stats]=ttest(contrst.(['S' parties{k} '_c' num2str(ConOrd) '_Tcurr'])(:,roi_ord2),contrst.(['S' parties{k} '_c' num2str(ConOrd) '_Tdelay'])(:,roi_ord2)); % paired t test
    ttest_results.(['S' parties{k} '_c' num2str(ConOrd)])(roi_ord2)=temp_p;
    ttest_stats.(['S' parties{k} '_c' num2str(ConOrd)])(roi_ord2,1)=temp_stats.tstat;
    ttest_stats.(['S' parties{k} '_c' num2str(ConOrd)])(roi_ord2,2)=temp_stats.df;
    ttest_stats.(['S' parties{k} '_c' num2str(ConOrd)])(roi_ord2,3)=temp_stats.sd;
end

%% FDR correction
for_fdr_pvalue=ttest_results.(['S' parties{k} '_c' num2str(ConOrd)]);
[temp_pID,temp_pN]=gretna_FDR(for_fdr_pvalue,0.05);
aft_fdr_corrected_status=zeros(length(ttest_results.(['S' parties{k} '_c' num2str(ConOrd)])),1);
if ~isempty(temp_pID)
    temp_fdr_status=for_fdr_pvalue<=temp_pID;
    aft_fdr_corrected_status=double(temp_fdr_status);
end



% for plot
n=n+1;
mean_curr=mean(contrst.(['S' parties{k} '_c' num2str(ConOrd) '_Tcurr']),1);
mean_delay=mean(contrst.(['S' parties{k} '_c' num2str(ConOrd) '_Tdelay']),1);
forplot_data=[mean_curr',mean_delay'];
figure(n);
b=bar(forplot_data);
hold on;


xtips1 = b(1).XEndPoints;
xtips2 = b(2).XEndPoints;

ytips1=b(1).YEndPoints;
ytips2=b(2).YEndPoints;
ytips=zeros(size(ytips1));

    for yOrd=1:length(ytips1)
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
        
        if ttest_results.(['S' parties{k} '_c' num2str(ConOrd)])(yOrd)<0.05 && aft_fdr_corrected_status(yOrd)==1
            plot([xtips1(yOrd),xtips2(yOrd)],[ytips(yOrd),ytips(yOrd)],'r-');
%             scatter((xtips1(yOrd)+xtips2(yOrd))/2,ytips(yOrd)+0.03,'**');
         text((xtips1(yOrd)+xtips2(yOrd))/2,label_pos,'**','FontSize',14);
        elseif ttest_results.(['S' parties{k} '_c' num2str(ConOrd)])(yOrd)<0.05 && aft_fdr_corrected_status(yOrd)==0
            plot([xtips1(yOrd),xtips2(yOrd)],[ytips(yOrd),ytips(yOrd)],'r-');
%             scatter((xtips1(yOrd)+xtips2(yOrd))/2,ytips(yOrd)+0.03,'*');
              text((xtips1(yOrd)+xtips2(yOrd))/2,label_pos,'*','FontSize',14);
        end
        
    end
    xticks(1:18);
    xticklabels(ROI_names);
    xtickangle(45);
    hold off;
 saveas(n,fullfile(workdir,['S' parties{k} '_c' num2str(ConOrd) '.png']),'png');

% if there are significant contrasts
  if any(ttest_results.(['S' parties{k} '_c' num2str(ConOrd)])<0.05)
      pvalue_status(ConOrd,k)=1;
  end


  end
end

output.tstat_df_sd= ttest_stats;
output.contrst_value=contrst;
output.contrast_name=CondNames;
output.ttest2_pvalue=ttest_results;
output.pvalue_status=pvalue_status;
% save(fullfile(workdir,'output_values.mat'),'output');
save(fullfile(workdir,'output_values_with_tstats.mat'),'output');