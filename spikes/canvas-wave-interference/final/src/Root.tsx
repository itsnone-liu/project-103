import React from 'react';
import {Composition} from 'remotion';
import {WaveInterferenceVideo} from './WaveInterferenceVideo';

export const FPS = 30;
export const DURATION = 1800;

export const RemotionRoot: React.FC = () => (
  <Composition id="WaveInterference" component={WaveInterferenceVideo} durationInFrames={DURATION} fps={FPS} width={1920} height={1080}/>
);
