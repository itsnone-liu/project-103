import React from 'react';
import {Composition} from 'remotion';
import {InventoryTurnoverVideo} from './Video';

export const FPS=30;
export const DURATION=6270;
export const RemotionRoot:React.FC=()=> <Composition id="InventoryTurnover" component={InventoryTurnoverVideo} durationInFrames={DURATION} fps={FPS} width={1920} height={1080}/>;
