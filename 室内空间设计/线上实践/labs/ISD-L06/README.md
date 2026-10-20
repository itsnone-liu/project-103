# ISD-L06 渲染层双档预演

用于判断 L06《空间围合与视线分析》的实时 3D 表达质量；不是正式教学实验。

- 基础档：Canvas 2D 软件透视，零外部依赖，`?offline=1` 强制启用。
- 增强档：Three.js r147 UMD + OrbitControls + RoomEnvironment，全部由 8861 同源静态托管；PBR 程序材质、ACES/sRGB、软阴影，可旋转、缩放、五个视点、剖切外墙、标注与 PNG 导出。
- 两档共享同一冻结 U90 MODEL 和相机预设；实时模型为教学级盒体家具，不是照片级静帧，尚未加入 HDRI、真实 PBR 纹理和 glTF 家具。
- QA：`python qa_run.py`；要求增强/基础两档均 6/6 自检、零控制台错误，增强档实际初始化而非伪装。

供应商资源：three.js 0.147.0，MIT；许可证见 `vendor/LICENSE-three.txt`。
