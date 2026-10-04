import React from 'react';
import {Composition} from 'remotion';
import {CapitalTurnoverVideo} from './Video';
export const RemotionRoot:React.FC=()=> <Composition id="CapitalTurnover" component={CapitalTurnoverVideo} durationInFrames={8400} fps={30} width={1920} height={1080}/>;
