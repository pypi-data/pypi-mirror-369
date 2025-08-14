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
#include <PxPhysicsAPI.h>
#include <memory>

namespace sapien {
namespace physx {
class PhysxEngine;

class PhysxMaterial : public std::enable_shared_from_this<PhysxMaterial> {
public:
  PhysxMaterial() : PhysxMaterial(0.f, 0.f, 0.f) {}
  PhysxMaterial(float dynamicFriction, float staticFriction, float restitution);

  inline ::physx::PxMaterial *getPxMaterial() const { return mMaterial; };

  inline float getStaticFriction() const { return mMaterial->getStaticFriction(); }
  inline float getDynamicFriction() const { return mMaterial->getDynamicFriction(); }
  inline float getRestitution() const { return mMaterial->getRestitution(); }

  inline void setStaticFriction(float coef) const { mMaterial->setStaticFriction(coef); }
  inline void setDynamicFriction(float coef) const { mMaterial->setDynamicFriction(coef); }
  inline void setRestitution(float coef) const { mMaterial->setRestitution(coef); }

  PhysxMaterial(PhysxMaterial const &other) = delete;
  PhysxMaterial &operator=(PhysxMaterial const &other) = delete;
  PhysxMaterial(PhysxMaterial &&other) = default;
  PhysxMaterial &operator=(PhysxMaterial &&other) = default;

  ~PhysxMaterial();

private:
  std::shared_ptr<PhysxEngine> mEngine;
  ::physx::PxMaterial *mMaterial;
};

} // namespace physx
} // namespace sapien
