/*
 * Copyright 2025 Hillbot Inc.
 * Copyright 2020-2024 UCSD SU Lab
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at:
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#pragma once
#include <memory>
#include <string>
#include <svulkan2/common/vk.h>
#include <svulkan2/renderer/rt_renderer.h>
#include <unordered_map>

namespace sapien {
namespace sapien_renderer {

class SapienRendererDefault {
public:
  static SapienRendererDefault &Get();

  static void setGlobalConfig(int32_t maxNumMaterials, uint32_t maxNumTextures,
                              uint32_t defaultMipMaps, bool doNotLoadTexture);

  static uint32_t getDefaultMipMaps();
  static bool getDoNotLoadTexture();
  static uint32_t getMaxNumMaterials();
  static uint32_t getMaxNumTextures();

  static void setImguiIniFilename(std::string const &filename);
  static std::string getImguiIniFilename();

  // vr
  static void setVRActionManifestFilename(std::string const &filename);
  static std::string getVRActionManifestFilename();
  static void enableVR();
  static bool getVREnabled();

  static void setViewerShaderDirectory(std::string const &dir);
  static void setCameraShaderDirectory(std::string const &dir);
  static void setRayTracingSamplesPerPixel(int spp);
  static void setRayTracingPathDepth(int depth);
  static void setRayTracingDenoiser(svulkan2::renderer::RTRenderer::DenoiserType type);
  static void setRayTracingDoFAperture(float radius);
  static void setRayTracingDoFPlane(float depth);
  static void setMSAA(int msaa);

  static std::string getViewerShaderDirectory();
  static std::string getCameraShaderDirectory();
  static int getRayTracingSamplesPerPixel();
  static int getRayTracingPathDepth();
  static svulkan2::renderer::RTRenderer::DenoiserType getRayTracingDenoiser();
  static float getRayTracingDoFAperture();
  static float getRayTracingDoFPlane();
  static int getMSAA();

  // TODO: set render target format
  static void setRenderTargetFormat(std::string const &name, vk::Format format);

  static void internalSetShaderSearchPath(std::string const &dir);

public:
  uint32_t defaultMipMaps = 1;
  bool doNotLoadTexture = false;
  uint32_t maxNumMaterials = 128;
  uint32_t maxNumTextures = 512;

  std::string viewerShaderDirectory{};
  std::string cameraShaderDirectory{};
  std::unordered_map<std::string, vk::Format> renderTargetFormats;
  int rayTracingSamplesPerPixel{32};
  int rayTracingPathDepth{8};
  int rayTracingRussianRouletteMinBounces{-1};
  svulkan2::renderer::RTRenderer::DenoiserType rayTracingDenoiserType{
      svulkan2::renderer::RTRenderer::DenoiserType::eNONE};
  int msaa{1};

  float rayTracingDoFAperture = 0.f;
  float rayTracingDoFPlane = 1.f;

  bool vrEnabled = false;

private:
  std::string shaderSearchPath;
};

} // namespace sapien_renderer
} // namespace sapien
