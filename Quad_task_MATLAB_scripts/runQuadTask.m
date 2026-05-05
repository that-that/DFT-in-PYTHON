 try 
    %add:  parPulse(portCode,1,0,255,.1); to put stim in fnirs
    %setup
    clearvars;
    clear global;
    clc;
    sca;
    rng('shuffle');
    
    %settings/parameters
    debugMode = 0; %set to 1 for small window
    nTrialsPerBlock = 30; % 30 trials = 2 passes of 15 sets
    
    itiMin = 2; 
    itiMax = 5; %randomized ITI
    
    shuffleImages = 1; %set to 1 to randomize left + right placement of image 1 + 2, 0 for fixed
    randomizeSetReplacement = 0; %0 = randomize w/o replacement (ensures 2 full passes), 1 = randomize w replacement
    
    baseDir = 'c:\Users\sbesh\Documents\scripts4matlab\quad_task';
    stimDir = fullfile(baseDir, 'stimulus');
    
    %block to file map
    blocks = {
        'phase 1 (dif shape dif color)', ...
        'phase 2 (same shape dif color)', ...
        'phase 3 (same color dif shape)', ...
        'phase 4 (same color same shape)'
    };
    
    %subj info
    prompt = {'Enter Subject Number:'};
    defaults = {'999'};
    answer = inputdlg(prompt, 'Subject Info', 1, defaults);
    
    if isempty(answer)
        return;
    end
    
    subNum = answer{1};
    startBlock = 1; % always start from beginning; phase order is shuffled per participant
    
    %get block order from subject number
    subSeed = str2double(subNum);
    if isnan(subSeed)
        subSeed = sum(double(subNum)); %if non-numeric sub number
    end
    prevRng = rng();
    rng(subSeed, 'twister');
    blockSequence = randperm(4);
    rng(prevRng); %re-randomize for trial randomization
    
    %output file
    outputFile = fullfile(baseDir, sprintf('S%s_QuadData.txt', subNum));
    if exist(outputFile, 'file')
        resp = questdlg('File exists. Overwrite?', 'Warning', 'Overwrite', 'Append', 'Cancel', 'Append');
        if strcmp(resp, 'Cancel')
            return;
        end
        fid = fopen(outputFile, 'a');
    else
        fid = fopen(outputFile, 'w');
        fprintf(fid, 'SubNum\tBlock\tTrial\tImageSet\tTargetSide\tTargetQuad\tAcc\tRT\tRespSide\tRespQuad\tITI\tProbeImg\tImgSwapped\n');
    end
    
    %ptb setup
    
    
    PsychDefaultSetup(2);
    Screen('Preference', 'SkipSyncTests', 1);
    screens = Screen('Screens');
    screenNumber = max(screens);
    %portCode = hex2dec('3FF8');
    %parPulse(portCode);
    
    if debugMode
        [window, windowRect] = PsychImaging('OpenWindow', screenNumber, [148/255 148/255 148/255], [0 0 800 600]);
    else
        [window, windowRect] = PsychImaging('OpenWindow', screenNumber, [148/255 148/255 148/255]);
    end
    Screen('TextSize', window, 40);
    HideCursor;
    
    %key maps
    KbName('UnifyKeyNames');
    keys.left = KbName('LeftArrow');
    keys.right = KbName('RightArrow');
    keys.esc = KbName('ESCAPE');
    keys.space = KbName('space');
    

    %experiment loop
    
   %practice phase
    if startBlock == 1
        DrawFormattedText(window, 'Practice Phase\n\nPress Space to begin practice.', 'center', 'center', [0 0 0]);
        Screen('Flip', window);
        KbStrokeWait;
        
        practiceTrials = 5;
        practiceStim = {};
        
        %right now one pic from each phase one duplicate
        for pb = 1:4
             pBlockName = blocks{pb};
             pStimDir = fullfile(stimDir, pBlockName);
             pFiles = dir(fullfile(pStimDir, '*.png'));
             pFileList = {pFiles.name};
             
             pSets = {};
             for k = 1:length(pFileList)
                tokens = regexp(pFileList{k}, '_(set\d+)_', 'tokens');
                if ~isempty(tokens)
                    pSets{end+1} = tokens{1}{1};
                end
             end
             pUniqueSets = unique(pSets);
             
             if ~isempty(pUniqueSets)
                 rndSet = pUniqueSets{randi(length(pUniqueSets))};
                 practiceStim{end+1} = struct('blockName', pBlockName, 'setName', rndSet);
             end
        end
        
        %
        if ~isempty(practiceStim)
            rndIdx = randi(length(practiceStim));
            practiceStim{end+1} = practiceStim{rndIdx};
        end
        
        practiceStim = practiceStim(randperm(length(practiceStim)));
        
        %run practice
        for iPTrial = 1:length(practiceStim)
            pConfig = practiceStim{iPTrial};
            pBlockDir = fullfile(stimDir, pConfig.blockName);
            pSet = pConfig.setName;
            
            %get images
            img1File = dir(fullfile(pBlockDir, sprintf('*%s_image1.png', pSet)));
            img2File = dir(fullfile(pBlockDir, sprintf('*%s_image2.png', pSet)));
            
             if isempty(img1File) || isempty(img2File)
                fprintf('Warning: Missing practice image pair for set %s. Skipping.\n', pSet);
                continue;
            end
            
            img1Data = imread(fullfile(pBlockDir, img1File(1).name));
            img2Data = imread(fullfile(pBlockDir, img2File(1).name));
             
            %shuffle left/right
            targetSide = randi(2); 
            targetQuad = randi(4);
            pSwapped = 0;
            if shuffleImages && rand > 0.5
                tempImg = img1Data;
                img1Data = img2Data;
                img2Data = tempImg;
                pSwapped = 1;
            end
            
            %determine which original image is the probe
            if pSwapped
                pProbeImg = 3 - targetSide; % swapped: side1->img2, side2->img1
            else
                pProbeImg = targetSide; % not swapped: side1->img1, side2->img2
            end
            
            tex1 = Screen('MakeTexture', window, img1Data);
            tex2 = Screen('MakeTexture', window, img2Data);
            
            
            iti = itiMin + (itiMax - itiMin) * rand;
            
            %run trial
            [acc, rt, response, ~] = QuadTaskTrial(window, tex1, tex2, targetSide, targetQuad, keys, iti);
            
            if numel(response) == 2
                rSide = response(1);
                rQuad = response(2);
            else
                rSide = NaN;
                rQuad = NaN;
            end
            
            %save data (block 0 = practice)
             fprintf(fid, '%s\t%d\t%d\t%s\t%d\t%d\t%d\t%.4f\t%d\t%d\t%.4f\t%d\t%d\n', ...
                subNum, 0, iPTrial, pSet, targetSide, targetQuad, acc, rt, rSide, rQuad, iti, pProbeImg, pSwapped);
            
            Screen('Close', tex1);
            Screen('Close', tex2);
        end
        
        DrawFormattedText(window, 'Practice Complete.\n\nPress Space to start the main experiment.', 'center', 'center', [0 0 0]);
        Screen('Flip', window);
        KbStrokeWait;
    end

    
    for iSeq = startBlock:4
        iBlock = blockSequence(iSeq);
        blockName = blocks{iBlock};
        curStimDir = fullfile(stimDir, blockName);
        
        %load img for block
        files = dir(fullfile(curStimDir, '*.png'));
        fileList = {files.name};
        
        %get set num
        sets = {};
        for k = 1:length(fileList)
            tokens = regexp(fileList{k}, '_(set\d+)_', 'tokens');
            if ~isempty(tokens)
                sets{end+1} = tokens{1}{1};
            end
        end
        uniqueSets = unique(sets);
        currentSetPool = uniqueSets;
        
        %start screen
        DrawFormattedText(window, sprintf('Block %d\n\nPress Space to Begin', iSeq), 'center', 'center', [0 0 0]);
        Screen('Flip', window);
        KbStrokeWait;
        
        for iTrial = 1:nTrialsPerBlock
            if isempty(uniqueSets)
                error('No images found in %s', curStimDir);
            end
            if randomizeSetReplacement == 1
                currSet = uniqueSets{randi(length(uniqueSets))};
            else
                if isempty(currentSetPool)
                    currentSetPool = uniqueSets;
                end
                idx = randi(length(currentSetPool));
                currSet = currentSetPool{idx};
                currentSetPool(idx) = [];
            end
            
            %get immg 1 & 2
            img1File = dir(fullfile(curStimDir, sprintf('*%s_image1.png', currSet)));
            img2File = dir(fullfile(curStimDir, sprintf('*%s_image2.png', currSet)));
            
            if isempty(img1File) || isempty(img2File)
                fprintf('Warning: Missing image pair for set %s in block %d. Skipping.\n', currSet, iBlock);
                continue;
            end
            
    %get textures
            img1Data = imread(fullfile(curStimDir, img1File(1).name));
            img2Data = imread(fullfile(curStimDir, img2File(1).name));

    %rand target
            targetSide = randi(2); % 1=L, 2=R
            targetQuad = randi(4); % 1=TL, 2=TR, 3=BL, 4=BR

    %shuffle img
            swapped = 0;
            if shuffleImages && rand > 0.5
                tempImg = img1Data;
                img1Data = img2Data;
                img2Data = tempImg;
                swapped = 1;
            end
            
            %determine which original image is the probe
            if swapped
                probeImg = 3 - targetSide; % swapped: side1->img2, side2->img1
            else
                probeImg = targetSide; % not swapped: side1->img1, side2->img2
            end

            tex1 = Screen('MakeTexture', window, img1Data);
            tex2 = Screen('MakeTexture', window, img2Data);
            iti = itiMin + (itiMax - itiMin) * rand;
            
            %start trial
            [acc, rt, response, ~] = QuadTaskTrial(window, tex1, tex2, targetSide, targetQuad, keys, iti);
            
            %response data
            if numel(response) == 2
                rSide = response(1);
                rQuad = response(2);
            else
                rSide = NaN;
                rQuad = NaN;
            end
            
            %save data
            fprintf(fid, '%s\t%d\t%d\t%s\t%d\t%d\t%d\t%.4f\t%d\t%d\t%.4f\t%d\t%d\n', ...
                subNum, iBlock, iTrial, currSet, targetSide, targetQuad, acc, rt, rSide, rQuad, iti, probeImg, swapped);
            
            %close texs
            Screen('Close', tex1);
            Screen('Close', tex2);
            
             %break(?)
            % if mod(iTrial, 10) == 0 && iTrial < nTrialsPerBlock
            %      DrawFormattedText(window, '[break txt]', 'center', 'center', [0 0 0]);
            %      Screen('Flip', window);
            %      WaitSecs(2);
            % end
        end
        
    end
    
    DrawFormattedText(window, 'Experiment Complete. Thank you!', 'center', 'center', [0 0 0]);
    Screen('Flip', window);
    WaitSecs(2);
    
    fclose(fid);
    sca;
    
catch me
    sca;
    if exist('fid', 'var')
        fclose(fid);
    end
    rethrow(me);
end
   