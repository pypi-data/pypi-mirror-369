#version 450
//
// Copyright 2025 Hillbot Inc.
// Copyright 2020-2024 UCSD SU Lab
// 
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at:
// 
//     http://www.apache.org/licenses/LICENSE-2.0
// 
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

layout(set = 0, binding = 0) uniform CameraBuffer {
  mat4 viewMatrix;
  mat4 projectionMatrix;
  mat4 viewMatrixInverse;
  mat4 projectionMatrixInverse;
  float width;
  float height;
} cameraBuffer;

layout(set = 1, binding = 0) uniform ObjectTransformBuffer {
  mat4 modelMatrix;
} objectTransformBuffer;

layout(set = 1, binding = 1) uniform ObjectDataBuffer {
  uvec4 segmentation;
  float transparency;
  int shadeFlat;
} objectDataBuffer;

layout(set = 2, binding = 0) uniform MaterialBuffer {
  vec4 emission;
  vec4 baseColor;
  float fresnel;
  float roughness;
  float metallic;
  float transmission;
  float ior;
  float transmissionRoughness;
  int textureMask;
  int padding1;
  vec4 textureTransforms[6];
} materialBuffer;

layout(set = 2, binding = 1) uniform sampler2D colorTexture;
layout(set = 2, binding = 2) uniform sampler2D roughnessTexture;
layout(set = 2, binding = 3) uniform sampler2D normalTexture;
layout(set = 2, binding = 4) uniform sampler2D metallicTexture;
layout(set = 2, binding = 5) uniform sampler2D emissionTexture;


struct PointLight {
  vec4 position;
  vec4 emission;
};

struct DirectionalLight {
  vec4 direction;
  vec4 emission;
};

struct SpotLight {
  vec4 position;
  vec4 direction;
  vec4 emission;
};

layout(set = 3, binding = 0) uniform SceneBuffer {
  vec4 ambientLight;
  DirectionalLight directionalLights[3];
  SpotLight spotLights[10];
  PointLight pointLights[10];
  SpotLight texturedLights[1];
} sceneBuffer;

layout(location = 0) in vec4 inPosition;
layout(location = 1) in vec2 inUV;
layout(location = 2) in flat uvec4 inSeg;

layout(location = 0) out vec4 outColor;
layout(location = 1) out vec4 outPosition;
layout(location = 2) out uvec4 outSegmentation;

void main() {
  outPosition = inPosition;
  outSegmentation = inSeg;
  if ((materialBuffer.textureMask & 1) != 0) {
    outColor = texture(colorTexture, inUV);
  } else {
    outColor = materialBuffer.baseColor;
  }
}