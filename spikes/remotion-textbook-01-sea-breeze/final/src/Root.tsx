import React from 'react';
import {Composition} from 'remotion';
import {SeaBreezeVideo} from './SeaBreezeVideo';

export const FPS = 30;
export const DURATION = 900;

export const RemotionRoot: React.FC = () => (
  <Composition
    id="SeaBreeze"
    component={SeaBreezeVideo}
    durationInFrames={DURATION}
    fps={FPS}
    width={1920}
    height={1080}
  />
);
