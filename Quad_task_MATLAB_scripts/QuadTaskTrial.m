%NOTES

%Change cursor color?: cursor gets lost often, made it center after each
%trial

%fix shuffle of stimulus-> random w/o replacement? same order for everyone
%etc.

%task is too hard imo... change to matching? increase encode time? show
%encode and probe together breifly then hide encode?

%trial cnt = 30. take 15 set make 2 random list of 15 run list back to
%back per phase


function [acc, rt, response, onsetTime] = QuadTaskTrial(window, tex1, tex2, targetSide, targetQuad, keys, iti)



    %settings/parameters
    EncodingTime = 4.0; 
    DelayTime = 0.25;   
    ProbeTime = 0.75;%grid appears AFTER
    MaxResponseTime = 7.0; 
    
    [screenXpixels, screenYpixels] = Screen('WindowSize', window);
    [xCenter, yCenter] = RectCenter([0 0 screenXpixels screenYpixels]);
    
    %stim locations:
    %assumes images are square(pls make it square)!
    leftPos = [xCenter - screenXpixels/4, yCenter - screenYpixels/4];
    rightPos = [xCenter + screenXpixels/4, yCenter - screenYpixels/4];
    
    %get imgs size
    %assumes tex1 and tex2 will be same size(pls mamke same size)!
    [imgW, imgH] = Screen('WindowSize', tex1);
    scaleFactor = 0.5; %scale value
    baseRect = [0 0 imgW*scaleFactor imgH*scaleFactor];
    
    %destination for rect
    dstRectLeft = CenterRectOnPointd(baseRect, leftPos(1), leftPos(2));
    dstRectRight = CenterRectOnPointd(baseRect, rightPos(1), rightPos(2));
    
    %probe prep
    srcRectFull = [0 0 imgW imgH]; 
    midW = imgW / 2;
    midH = imgH / 2;
    
    if targetQuad == 1 %topL
        srcRect = [0, 0, midW, midH];
    elseif targetQuad == 2 %topR
        srcRect = [midW, 0, imgW, midH];
    elseif targetQuad == 3 %bottommL
        srcRect = [0, midH, midW, imgH];
    elseif targetQuad == 4 %bottomR
        srcRect = [midW, midH, imgW, imgH];
    end
    
    %probe location
    %&scale up probe
    probeRect = [0 0 midW*scaleFactor midH*scaleFactor];
    dstRectProbe = CenterRectOnPointd(probeRect, xCenter, yCenter + screenYpixels/4);
    
    if targetSide == 1
        targetTex = tex1;
    else
        targetTex = tex2;
    end
    
    %itiDelay + center dot
    Screen('DrawDots', window, [xCenter, yCenter], 10, [0 0 0], [], 2);
    Screen('Flip', window);
    WaitSecs(iti);
    
    %encode
    Screen('DrawTexture', window, tex1, [], dstRectLeft);
    Screen('DrawTexture', window, tex2, [], dstRectRight);
    %parPulse(portCode,1,0,255,.15);
    onsetTime = Screen('Flip', window);
    
    WaitSecs(EncodingTime);
    
    %delay
    Screen('DrawDots', window, [xCenter, yCenter], 10, [0 0 0], [], 2); 
    Screen('Flip', window);
    WaitSecs(DelayTime);
    
    %probe
    Screen('DrawTexture', window, targetTex, srcRect, dstRectProbe);
    probeOnset = Screen('Flip', window);
    WaitSecs(ProbeTime); %delay
    SetMouse(xCenter, yCenter);
    
    %response
    Screen('FrameRect', window, [0 0 0], dstRectLeft, 2);
    Screen('FrameRect', window, [0 0 0], dstRectRight, 2);
    
    %draw quad lines left
    Screen('DrawLine', window, [0 0 0], leftPos(1), dstRectLeft(2), leftPos(1), dstRectLeft(4), 2);
    Screen('DrawLine', window, [0 0 0], dstRectLeft(1), leftPos(2), dstRectLeft(3), leftPos(2), 2);
    
    %draw quad lines right
    Screen('DrawLine', window, [0 0 0], rightPos(1), dstRectRight(2), rightPos(1), dstRectRight(4), 2);
    Screen('DrawLine', window, [0 0 0], dstRectRight(1), rightPos(2), dstRectRight(3), rightPos(2), 2);
    
    %draw probe for response
    Screen('DrawTexture', window, targetTex, srcRect, dstRectProbe);
    
    %cursor displayed
    ShowCursor('Arrow');
    
    respOnset = Screen('Flip', window);
    
    respToBeMade = true;
    tStart = GetSecs;
    response = NaN;
    rt = NaN;
    
    %click zones
    %left zones
    L_Q1 = [dstRectLeft(1), dstRectLeft(2), leftPos(1), leftPos(2)]; % TL
    L_Q2 = [leftPos(1), dstRectLeft(2), dstRectLeft(3), leftPos(2)]; % TR
    L_Q3 = [dstRectLeft(1), leftPos(2), leftPos(1), dstRectLeft(4)]; % BL
    L_Q4 = [leftPos(1), leftPos(2), dstRectLeft(3), dstRectLeft(4)]; % BR
    
    %right zones
    R_Q1 = [dstRectRight(1), dstRectRight(2), rightPos(1), rightPos(2)]; % TL
    R_Q2 = [rightPos(1), dstRectRight(2), dstRectRight(3), rightPos(2)]; % TR
    R_Q3 = [dstRectRight(1), rightPos(2), rightPos(1), dstRectRight(4)]; % BL
    R_Q4 = [rightPos(1), rightPos(2), dstRectRight(3), dstRectRight(4)]; % BR
    
    while respToBeMade && (GetSecs - tStart < MaxResponseTime)
        [x, y, buttons] = GetMouse(window);
        
        %ESC to abort
        [keyIsDown, ~, keyCode] = KbCheck;
        if keyIsDown && keyCode(keys.esc)
            sca; error('User aborted');
        end
        
        if any(buttons)
            %Left?
            if IsInRect(x, y, L_Q1);     response = [1, 1];
            elseif IsInRect(x, y, L_Q2); response = [1, 2];
            elseif IsInRect(x, y, L_Q3); response = [1, 3];
            elseif IsInRect(x, y, L_Q4); response = [1, 4];
                
            %Right?
            elseif IsInRect(x, y, R_Q1); response = [2, 1];
            elseif IsInRect(x, y, R_Q2); response = [2, 2];
            elseif IsInRect(x, y, R_Q3); response = [2, 3];
            elseif IsInRect(x, y, R_Q4); response = [2, 4];
            end
            
            if ~isnan(response)
                rt = GetSecs - respOnset;
                respToBeMade = false;
            end
        end
    end
    
    HideCursor;
    
    if isnan(response)%no response? -> NAN -> -1 val
        acc = -1;
    else
        %correct choice?
        if response(1) == targetSide && response(2) == targetQuad
            acc = 1;
        else
            acc = 0;
        end
    end
    
    Screen('Flip', window); %clear screen
    
end
