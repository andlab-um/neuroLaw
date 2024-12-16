clc
%% performing prediction with MVPA for Jiamin  Yuwen 202408
path.data='F:\Jiamin\SingleTrial';
path.beh='D:\OneDrive - zzu.edu.cn\Involved Study\Neurolaw\Info';
path.roi='D:\OneDrive - zzu.edu.cn\Involved Study\Neurolaw\fMRI analysis\ROI_MVPA';
% Subjects
num.chars = 2; % # of characters to consider
subject = struct2cell(dir(path.data))'; % list folder content
subject = char(subject(:, 1)); % convert to string
subject(subject(:, 1) == '.', :) = []; % find hidden folders/files (starting with '.') and delete
num.subjects = size(subject, 1); % # of subjects
subject = cellstr(subject); % make cell array (for convenience)

%% load ROIs
ROIs=spm_select('List',path.roi,'.nii');
ROIs=cellstr(ROIs);

for roi_ord=1:length(ROIs)
    roi_v=spm_vol(fullfile(path.roi,ROIs{roi_ord}));
    roi_img=spm_read_vols(roi_v);
    ROIimage.(['r' num2str(roi_ord)])=roi_img;
end

%% 4D_delayed-1_Sess001.nii
cat_names={'current-3','current-2','current-1','delayed-3','delayed-2','delayed-1'};
unique_cat=[-3,-2,-1,3,2,1];
accuracy_predicted=zeros(length(subject),2);
for i = 1:length(subject)

    % behavioral data
    condition.rawdata = readtable(fullfile(path.beh, [subject{i} '_neurolaw.xlsx']), 'FileType', 'spreadsheet');
    
    BehInfo=[condition.rawdata.Category,condition.rawdata.TimeLength,condition.rawdata.Rating];
    BehInfo(isnan(BehInfo(:,1)),:)=[];   % 1st column, category, 2nd: C
    temp_TimeLength=BehInfo(:,2);
    temp_TimeLength(temp_TimeLength>0)=1;
    temp_TimeLength(temp_TimeLength==0)=-1;


   category=BehInfo(:,1);
   category=category.*temp_TimeLength;
   %
   rating=BehInfo(:,3);

   arranged_rating=zeros(9,6);
   image_current=[];
   image_delay=[];

   for k=1:size(arranged_rating,2)
      temp_rating=rating(category==unique_cat(k)); 
      arranged_rating(:,k)=temp_rating;
     %
     temp_v=spm_vol(fullfile(path.data,subject{i},'betas',['4D_' cat_names{k} '_Sess001.nii']));
     temp_img=spm_read_vols(temp_v);
     if k<4
       image_current=cat(4,image_current,temp_img);
     elseif k>3 && k<7
        image_delay=cat(4,image_delay,temp_img); 
     end


   end

rate_current=arranged_rating(:,1:3);
rate_current=reshape(rate_current,[numel(rate_current),1]);
rate_current(rate_current<5)=-1;
rate_current(rate_current>=5)=1;

rate_delay=arranged_rating(:,4:6);
rate_delay=reshape(rate_delay,[numel(rate_delay),1]);
rate_delay(rate_delay<5)=-1;
rate_delay(rate_delay>=5)=1;

%% extract roi data
image_current_mat=zeros(size(image_current,4),length(ROIs));
image_delay_mat=zeros(size(image_current,4),length(ROIs));
for roi_ord2=1:length(ROIs)
    
    for rate_ord=1:size(image_current,4)
    temp_current=image_current(:,:,:,rate_ord);
    image_current_mat(rate_ord,roi_ord2)=mean(temp_current(ROIimage.(['r' num2str(roi_ord2)])>0),'all','omitnan');
    %
    temp_delay=image_delay(:,:,:,rate_ord);
    image_delay_mat(rate_ord,roi_ord2)=mean(temp_delay(ROIimage.(['r' num2str(roi_ord2)])>0),'all','omitnan');
    end
    %
    cfg.sample_dimension=1;
    cfg.feature_dimension=2;
    % cfg.generalization_dimension=2;
    cfg.dimension_names={'sample','ROIs'};
    cfg.cv='kfold';
    cfg.k=5;
    cfg.classifier='lda'; % naive_bayes multiclass_lda ensemble    
    [perf_current, result_current, testlabel_current] = mv_classify(cfg,image_current_mat, rate_current);
    [perf_delay, result_delay, testlabel_delay] = mv_classify(cfg,image_delay_mat, rate_delay);
    accuracy_predicted(i,1)=perf_current;
    accuracy_predicted(i,2)=perf_delay;
end




end


