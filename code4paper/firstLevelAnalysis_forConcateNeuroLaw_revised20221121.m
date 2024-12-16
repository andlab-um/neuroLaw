%% first level analysis for Jiamin written by Yuwen 20211124

clear all;
% addpath(genpath('/DISKA/OWEN/NeuroImageSoftwares'));
% Paths
path.root = 'G:\';
path.info = fullfile(path.root, 'Info');
path.data='G:\DAPBIData\Concated_ARWS';
path.preprocessd = fullfile(path.root, 'DAPBIData');
path.FunImg = fullfile(path.preprocessd, 'FunImg');
fname = 'dswa_4D_wds.nii'; % filename of func. imgs
% path.spm = fullfile(path.root, 'Analysis_Num\1stlevel_dswa'); % output folder
% path.nvrmask = fullfile(path.root, 'nvrMasks'); % path to prespecified brain mask (if used)
% nvrprefix = 'nvr'; % same prefix for all NVRs!

% Options
opt.PreBrainMask = 0; % whether or not to use a previously
% generated brain mask (e.g., from
% segmentation)
opt.unit = 'secs'; % timing units. 'scans' or 'secs'
opt.TR = 1; % repetition time (in seconditions)
opt.fmri_t = 65; % microtime resolution (default = 16). Timebins per scans when building regressors
opt.fmri_t0 = 33; % microtime onset (default = 8). Reference timebin

opt.HighPassFilter = 128; % highpass filter. 'Inf' to disable
opt.autocor = 'AR(1)'; % serial correlations in time series: 'AR(1)' or 'none'
nsession = 10;
nsessionTiming = 3;
nsessionJudgement = 1;
nsessionNeurolaw = 6;

% Conditions
% condition(1).name  = '0-Back';
% condition(1).onset = [6; 42; 60; 132; 150; 204];
% condition(1).dur   = 12;
% condition(2).name  = '2-Back';
% condition(2).onset = [24; 78; 96; 114; 168; 186];
% condition(2).dur   = 12;
% condition(3).name  = 'Cue';
% condition(3).onset = [5; 23; 41; 59; 77; 95; 113; 131; 149; 167; 185; 203];
% condition(3).dur   = 1;
% Subjects
num.chars = 2; % # of characters to consider
subject = struct2cell(dir(path.FunImg))'; % list folder content
subject = char(subject(:, 1)); % convert to string
subject(subject(:, 1) == '.', :) = []; % find hidden folders/files (starting with '.') and delete
num.subjects = size(subject, 1); % # of subjects
subject = cellstr(subject); % make cell array (for convenience)

 maskDir='G:\DAPBIData\Masks\AllResampled_GreyMask_02_91x109x91.nii';

% Initialize SPM
spm('Defaults', 'fMRI');
spm_jobman('initcfg');

%% LOAD Time points for each run

TimeP_forEachRun=load(fullfile(path.info,'TpointsInfo.mat'));
TimeP_forEachRun=TimeP_forEachRun.TimePointsForEachRun;

runSet = {'Run1', 'Run2', 'Run3', 'Run4', 'Run5', 'Run6'};

for i = 1:length(subject)

 clear matlabbatch
            workingDir = fullfile(path.root, 'Results', 'firstLevel_neurolaw_concated_revised20221121',subject{i});

            if ~exist(workingDir, 'dir')
                mkdir(workingDir);
            else
            end

            % run label
            condition.rawdata = readtable(fullfile(path.info, [subject{i} '_neurolaw.xlsx']), 'FileType', 'spreadsheet');
            runlabels = condition.rawdata.RunLable;
            [~, AinBindex] = ismember(runlabels, runSet);  % run label
            runNum = unique(AinBindex);
            % initiate head motion variable
           Headmotion_allRun=[];
           % category, time length, rating
            temp_TimeLength=condition.rawdata.TimeLength;
            temp_TimeLength(isnan(temp_TimeLength))=[];
            temp_TimeLength=temp_TimeLength>0;
            temp_TimeLength=double(temp_TimeLength);
            
            BehInfo=[condition.rawdata.Category,condition.rawdata.TimeLength,condition.rawdata.Rating];
            BehInfo(isnan(BehInfo(:,1)),:)=[];   % 1st column, category, 2nd: C
            BehInfo(:,2)=temp_TimeLength;
            
            % run info
            matlabbatch{1}.spm.stats.fmri_spec.dir = {workingDir};
            matlabbatch{1}.spm.stats.fmri_spec.timing.units = opt.unit;
            matlabbatch{1}.spm.stats.fmri_spec.timing.RT = opt.TR;
            matlabbatch{1}.spm.stats.fmri_spec.timing.fmri_t = opt.fmri_t;
            matlabbatch{1}.spm.stats.fmri_spec.timing.fmri_t0 = opt.fmri_t0;

            matlabbatch{1}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});
            matlabbatch{1}.spm.stats.fmri_spec.bases.hrf.derivs = [0 0];
            matlabbatch{1}.spm.stats.fmri_spec.volt = 1;
            matlabbatch{1}.spm.stats.fmri_spec.global = 'None';
            matlabbatch{1}.spm.stats.fmri_spec.mthresh = 0.8;
            matlabbatch{1}.spm.stats.fmri_spec.mask = {''};
            matlabbatch{1}.spm.stats.fmri_spec.cvi = 'AR(1)';

            
%             NeuroLawCheckOnset=[];
%             NeuroLawCheckDuration=[];
            for RunOrd = 1:length(runNum)
                IndRun = find(AinBindex == RunOrd);
                RUN.(['triggerOn_' num2str(RunOrd)]) = condition.rawdata.TextReady_RTTime(IndRun(1));
                RUN.(['triggerOn_' num2str(RunOrd)]) = RUN.(['triggerOn_' num2str(RunOrd)]) / 1000;
                %          RUN.(['triggerOn_' num2str(RunOrd)])=double(RUN.(['triggerOn_' num2str(RunOrd)]));
              
                    RUN.(['blankOnset_' num2str(RunOrd)]) = condition.rawdata.check_OnsetTime;
                    RUN.(['blankOnset_' num2str(RunOrd)]) = RUN.(['blankOnset_' num2str(RunOrd)])(IndRun);
                    RUN.(['blankOnset_' num2str(RunOrd)])(1, :) = [];
                    RUN.(['blankOnset_' num2str(RunOrd)]) = RUN.(['blankOnset_' num2str(RunOrd)]) / 1000;
                
                    % minus onset
                    RUN.(['blankOnset_' num2str(RunOrd)]) = RUN.(['blankOnset_' num2str(RunOrd)]) - RUN.(['triggerOn_' num2str(RunOrd)]);

                    % duration
                    RUN.(['blankDuration_' num2str(RunOrd)]) = condition.rawdata.check_RTTime;
                    RUN.(['blankDuration_' num2str(RunOrd)]) = RUN.(['blankDuration_' num2str(RunOrd)])(IndRun);
                    RUN.(['blankDuration_' num2str(RunOrd)])(1, :) = [];
                    RUN.(['blankDuration_' num2str(RunOrd)]) = RUN.(['blankDuration_' num2str(RunOrd)]) / 1000;

                    %          RUN.(['blankDuration_' num2str(RunOrd) '_' num2str(CondOrd)])=cell2mat(RUN.(['blankDuration_' num2str(RunOrd) '_' num2str(CondOrd)]));
                    RUN.(['blankDuration_' num2str(RunOrd)]) = RUN.(['blankDuration_' num2str(RunOrd)]) - RUN.(['blankOnset_' num2str(RunOrd)]);
                    RUN.(['blankDuration_' num2str(RunOrd)]) = RUN.(['blankDuration_' num2str(RunOrd)]) - RUN.(['triggerOn_' num2str(RunOrd)]);

                    if RunOrd ==1
                       NeuroLawCheckOnset=  RUN.(['blankOnset_' num2str(RunOrd)]);
                       NeuroLawCheckDuration=RUN.(['blankDuration_' num2str(RunOrd)]);
                    else
                        temp_blankOnset=RUN.(['blankOnset_' num2str(RunOrd)]) + sum(TimeP_forEachRun(i,1:RunOrd-1),'all');
                        NeuroLawCheckOnset=[NeuroLawCheckOnset;temp_blankOnset];
                        NeuroLawCheckDuration=[NeuroLawCheckDuration;RUN.(['blankDuration_' num2str(RunOrd)])];
                    end
            
                    
                    
                    % regressors  %%%%%%%%%%%% Pending to resolve%%%%%%%%%%%%%%%%%%%
                headDir = spm_select('FPList', fullfile(path.preprocessd, 'RealignParameter', subject{i}), ['^S' num2str(RunOrd + 4) '_rp_a.*']);
                disp(['headDir: ' headDir]);
                fid = fopen(headDir, 'r');
                temp_hdm = textscan(fid, '%32f%32f%32f%32f%32f%32f');
                headmotion.(['RUN' num2str(RunOrd)]) = [];

                for hdmNum = 1:length(temp_hdm)
                    headmotion.(['RUN' num2str(RunOrd)]) = cat(2, headmotion.(['RUN' num2str(RunOrd)]), temp_hdm{1, hdmNum});
                end

                fclose(fid);
                %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                %          PCA_reg=load();
                
%                 R = headmotion.(['RUN' num2str(RunOrd)]);
%                 save(fullfile(workingDir, [subject{i} 'run' num2str(RunOrd) '_regrs.mat']), 'R');
            Headmotion_allRun=cat(1,Headmotion_allRun,headmotion.(['RUN' num2str(RunOrd)]));
            end
            
            % headmotion
            R=Headmotion_allRun;
            save(fullfile(workingDir, [subject{i} 'All run_regrs.mat']), 'R');
            
          All_condition=[1,0;2,0;3,0;1,1;2,1;3,1];
          cat_currentOrNot=BehInfo(:,1:2);
          
          Rating=BehInfo(:,3);
          RunOrd=1;
           
          CondNames={'current-1','current-2','current-3','delayed-1','delayed-2','delayed-3'};

                for CondOrd = 1:length(All_condition)
                    ConInd=ismember(cat_currentOrNot,All_condition(CondOrd,:),'row');
                    
                    
                    
                    %onset
                  RUN.(['blankOnset_' num2str(CondOrd)]) =NeuroLawCheckOnset(ConInd);
                  %duration
                  RUN.(['blankDuration_' num2str(CondOrd)]) =NeuroLawCheckDuration(ConInd);
                    
                  


                    % condition matlabbatch
                    matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).cond(CondOrd).name = CondNames{CondOrd};
                    matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).cond(CondOrd).onset = RUN.(['blankOnset_' num2str(CondOrd)]);
                    matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).cond(CondOrd).duration =  RUN.(['blankDuration_' num2str(CondOrd)]);
                    matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).cond(CondOrd).tmod = 0;
                    % matlabbatch{1}.spm.stats.fmri_spec.sess(1).cond.pmod = struct('name', {}, 'param', {}, 'poly', {});
                    matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).cond(CondOrd).orth = 0; % without orthogazation
                   matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).cond(CondOrd).pmod = struct('name', {}, 'param', {}, 'poly', {});
%                     % trial parameteric
%                     % behavior
%                    
%                     beh_1.(['RUN_' num2str(RunOrd) '_' num2str(CondOrd)])=Rating(ConInd);
%                    
% 
%                    para_beh.(['RUN_' num2str(RunOrd) '_' num2str(CondOrd)]) = [beh_1.(['RUN_' num2str(RunOrd) '_' num2str(CondOrd)])];
%                      
% %                     para_name = {'rating', 'category', 'TimeLength'};
%                      para_name = {'rating'};
% 
%                     for paraOrd = 1:size(para_beh.(['RUN_' num2str(RunOrd) '_' num2str(CondOrd)]), 2)
%                         matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).cond(CondOrd).pmod(paraOrd).name = para_name{paraOrd};
%                         matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).cond(CondOrd).pmod(paraOrd).param = para_beh.(['RUN_' num2str(RunOrd) '_' num2str(CondOrd)])(:, paraOrd);
%                         matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).cond(CondOrd).pmod(paraOrd).poly = 1;
%                     end

                end % condtions CondOrd

                % Images
                Run.(['Image_' num2str(RunOrd)]) = spm_select('ExtFPList', fullfile(path.data, subject{i}), '.nii', Inf);
                Run.(['Image_' num2str(RunOrd)]) = cellstr(Run.(['Image_' num2str(RunOrd)]));

                % conditions

%                 % regressors  %%%%%%%%%%%% Pending to resolve%%%%%%%%%%%%%%%%%%%
%                 headDir = spm_select('FPList', fullfile(path.preprocessd, 'RealignParameter', subject{i}), ['^S' num2str(RunOrd + 4) '_rp_a.*']);
%                 disp(['headDir: ' headDir]);
%                 fid = fopen(headDir, 'r');
%                 temp_hdm = textscan(fid, '%32f%32f%32f%32f%32f%32f');
%                 headmotion.(['RUN' num2str(RunOrd)]) = [];
% 
%                 for hdmNum = 1:length(temp_hdm)
%                     headmotion.(['RUN' num2str(RunOrd)]) = cat(2, headmotion.(['RUN' num2str(RunOrd)]), temp_hdm{1, hdmNum});
%                 end
% 
%                 fclose(fid);
%                 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                 %          PCA_reg=load();
%                 R = headmotion.(['RUN' num2str(RunOrd)]);
%                 save(fullfile(workingDir, [subject{i} 'run' num2str(RunOrd) '_regrs.mat']), 'R');

                %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).scans = Run.(['Image_' num2str(RunOrd)]);

                matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).multi = {''};
                matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).regress = struct('name', {}, 'val', {});
                matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).multi_reg = {fullfile(workingDir, [subject{i} 'All run_regrs.mat'])};
                matlabbatch{1}.spm.stats.fmri_spec.sess(RunOrd).hpf = 128;
%             end

            % model estimation contrast
            matlabbatch{2}.spm.stats.fmri_est.spmmat(1) = cfg_dep('fMRI model specification: SPM.mat File', substruct('.', 'val', '{}', {1}, '.', 'val', '{}', {1}, '.', 'val', '{}', {1}), substruct('.', 'spmmat'));
            matlabbatch{2}.spm.stats.fmri_est.write_residuals = 0;
            matlabbatch{2}.spm.stats.fmri_est.method.Classical = 1;
            matlabbatch{3}.spm.stats.con.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.', 'val', '{}', {2}, '.', 'val', '{}', {1}, '.', 'val', '{}', {1}), substruct('.', 'spmmat'));
            matlabbatch{3}.spm.stats.con.consess{1}.tcon.name = 'current';
            matlabbatch{3}.spm.stats.con.consess{1}.tcon.weights = [1/3 1/3 1/3];
            matlabbatch{3}.spm.stats.con.consess{1}.tcon.sessrep = 'none';
            matlabbatch{3}.spm.stats.con.consess{2}.tcon.name = 'delayed';
            matlabbatch{3}.spm.stats.con.consess{2}.tcon.weights = [zeros(1,3),1/3, 1/3, 1/3];
            matlabbatch{3}.spm.stats.con.consess{2}.tcon.sessrep = 'none';
            matlabbatch{3}.spm.stats.con.consess{3}.tcon.name = 'current-delayed';
            matlabbatch{3}.spm.stats.con.consess{3}.tcon.weights = [1/3, 1/3, 1/3,-1/3, -1/3, -1/3];
            matlabbatch{3}.spm.stats.con.consess{3}.tcon.sessrep = 'none';
            matlabbatch{3}.spm.stats.con.consess{4}.tcon.name = 'cat1';
            matlabbatch{3}.spm.stats.con.consess{4}.tcon.weights = [0.5 zeros(1, 2) 0.5];
            matlabbatch{3}.spm.stats.con.consess{4}.tcon.sessrep = 'none';
            matlabbatch{3}.spm.stats.con.consess{5}.tcon.name = 'cat2';
            matlabbatch{3}.spm.stats.con.consess{5}.tcon.weights = [0 0.5 zeros(1, 2) 0.5];
            matlabbatch{3}.spm.stats.con.consess{5}.tcon.sessrep = 'none';
            matlabbatch{3}.spm.stats.con.consess{6}.tcon.name = 'cat3';
            matlabbatch{3}.spm.stats.con.consess{6}.tcon.weights = [0 0 0.5 zeros(1, 2) 0.5];
            matlabbatch{3}.spm.stats.con.consess{6}.tcon.sessrep = 'none';
%             matlabbatch{3}.spm.stats.con.consess{2}.tcon.name = 'Rating';
%             matlabbatch{3}.spm.stats.con.consess{2}.tcon.weights = [0 1];
%             matlabbatch{3}.spm.stats.con.consess{2}.tcon.sessrep = 'replsc';
%             matlabbatch{3}.spm.stats.con.consess{3}.tcon.name = 'category';
%             matlabbatch{3}.spm.stats.con.consess{3}.tcon.weights = [0 0 1];
%             matlabbatch{3}.spm.stats.con.consess{3}.tcon.sessrep = 'replsc';
%             matlabbatch{3}.spm.stats.con.consess{4}.tcon.name = 'Time Length';
%             matlabbatch{3}.spm.stats.con.consess{4}.tcon.weights = [0 0 0 1];
%             matlabbatch{3}.spm.stats.con.consess{4}.tcon.sessrep = 'replsc';
%             matlabbatch{3}.spm.stats.con.consess{5}.tcon.name = 'PM cur rating> delayed rating';
%             matlabbatch{3}.spm.stats.con.consess{5}.tcon.weights = [0 1 zeros(1, 3) -1];
%             matlabbatch{3}.spm.stats.con.consess{5}.tcon.sessrep = 'replsc';
            %      matlabbatch{3}.spm.stats.con.consess{6}.tcon.name    = 'PM time length';
            %     matlabbatch{3}.spm.stats.con.consess{6}.tcon.weights = [0 0 0 0 1/6 zeros(1,6) 0 0 0 0 1/6 zeros(1,6) 0 0 0 0 1/6 zeros(1,6) 0 0 0 0 1/6 zeros(1,6) 0 0 0 0 1/6 zeros(1,6) 0 0 0 0 1/6 zeros(1,6)];
            %     matlabbatch{3}.spm.stats.con.consess{6}.tcon.sessrep = 'none';
            matlabbatch{3}.spm.stats.con.delete = 0;
            % run
            spm_jobman('run', matlabbatch);
            clear RUN headmotion beh_1 beh_2 beh_2 para_beh Run
            fprintf('\n %s finished!',subject{i});
end