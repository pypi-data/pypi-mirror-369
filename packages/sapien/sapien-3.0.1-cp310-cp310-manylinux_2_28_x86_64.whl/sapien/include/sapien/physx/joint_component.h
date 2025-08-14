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
#include "base_component.h"
#include "rigid_component.h"
#include "sapien/math/conversion.h"

namespace sapien {
class Entity;
namespace physx {

class PhysxJointComponent : public PhysxBaseComponent {
public:
  PhysxJointComponent(std::shared_ptr<PhysxRigidBodyComponent> body);

  /** should be called internally when PxActor changes for parent or child */
  virtual void internalRefresh();

  void onAddToScene(Scene &scene) override;
  void onRemoveFromScene(Scene &scene) override;

  void setParent(std::shared_ptr<PhysxRigidBaseComponent> body);
  std::shared_ptr<PhysxRigidBaseComponent> getParent() const;

  void setParentAnchorPose(Pose const &pose);
  Pose getParentAnchorPose() const;
  void setChildAnchorPose(Pose const &pose);
  Pose getChildAnchorPose() const;

  Pose getRelativePose() const;

  // TODO: serialize
  void setInvMassScales(float, float);
  void setInvInertiaScales(float, float);

  virtual ::physx::PxJoint *getPxJoint() const = 0;
  ~PhysxJointComponent();

protected:
  std::shared_ptr<PhysxRigidBodyComponent> mChild;
  std::shared_ptr<PhysxRigidBaseComponent> mParent;
};

class PhysxDriveComponent : public PhysxJointComponent {
public:
  enum class DriveMode { eFORCE, eACCELERATION };

  static std::shared_ptr<PhysxDriveComponent>
  Create(std::shared_ptr<PhysxRigidBodyComponent> body);

  /** should only be called internally */
  PhysxDriveComponent(std::shared_ptr<PhysxRigidBodyComponent> body);

  void setXLimit(float low, float high, float stiffness, float damping);
  void setYLimit(float low, float high, float stiffness, float damping);
  void setZLimit(float low, float high, float stiffness, float damping);
  void setXTwistLimit(float low, float high, float stiffness, float damping);
  void setYZConeLimit(float yAngle, float zAngle, float stiffness, float damping);
  void setYZPyramidLimit(float yLow, float yHigh, float zLow, float zHigh, float stiffness,
                         float damping);

  std::tuple<float, float, float, float> getXLimit() const;
  std::tuple<float, float, float, float> getYLimit() const;
  std::tuple<float, float, float, float> getZLimit() const;
  std::tuple<float, float, float, float> getXTwistLimit() const;
  std::tuple<float, float, float, float> getYZConeLimit() const;
  std::tuple<float, float, float, float, float, float> getZPyramidLimit() const;

  void setXDriveProperties(float stiffness, float damping, float forceLimit, DriveMode mode);
  void setYDriveProperties(float stiffness, float damping, float forceLimit, DriveMode mode);
  void setZDriveProperties(float stiffness, float damping, float forceLimit, DriveMode mode);
  void setXTwistDriveProperties(float stiffness, float damping, float forceLimit, DriveMode mode);
  void setYZSwingDriveProperties(float stiffness, float damping, float forceLimit, DriveMode mode);
  void setSlerpDriveProperties(float stiffness, float damping, float forceLimit, DriveMode mode);

  std::tuple<float, float, float, DriveMode> getXDriveProperties() const;
  std::tuple<float, float, float, DriveMode> getYDriveProperties() const;
  std::tuple<float, float, float, DriveMode> getZDriveProperties() const;
  std::tuple<float, float, float, DriveMode> getXTwistDriveProperties() const;
  std::tuple<float, float, float, DriveMode> getYZSwingDriveProperties() const;
  std::tuple<float, float, float, DriveMode> getSlerpDriveProperties() const;

  void setDriveTarget(Pose const &pose);
  Pose getDriveTarget() const;

  void setDriveTargetVelocity(Vec3 const &linear, Vec3 const &angular);
  std::tuple<Vec3, Vec3> getDriveTargetVelocity() const;

  ::physx::PxJoint *getPxJoint() const override { return mJoint; }

  ~PhysxDriveComponent();

private:
  void setLinearLimit(::physx::PxD6Axis::Enum axis, float low, float high, float stiffness,
                      float damping);
  void setDrive(::physx::PxD6Drive::Enum drive, float stiffness, float damping, float forceLimit,
                DriveMode mode);

  ::physx::PxD6Joint *mJoint;
};

class PhysxGearComponent : public PhysxJointComponent {

public:
  static std::shared_ptr<PhysxGearComponent> Create(std::shared_ptr<PhysxRigidBodyComponent> body);

  /** should only be called internally */
  PhysxGearComponent(std::shared_ptr<PhysxRigidBodyComponent> body);

  float getGearRatio() const;
  void setGearRatio(float ratio);

  void enableHinges();
  bool getHingesEnabled() const { return mHingesEnabled; };

  ::physx::PxJoint *getPxJoint() const override { return mJoint; }

  void internalRefresh() override;

  ~PhysxGearComponent();

private:
  bool mHingesEnabled{false};
  ::physx::PxGearJoint *mJoint;
};

class PhysxDistanceJointComponent : public PhysxJointComponent {
public:
  static std::shared_ptr<PhysxDistanceJointComponent>
  Create(std::shared_ptr<PhysxRigidBodyComponent> body);
  PhysxDistanceJointComponent(std::shared_ptr<PhysxRigidBodyComponent> body);

  void setLimit(float low, float high, float stiffness, float damping);
  float getStiffness() const;
  float getDamping() const;
  Eigen::Vector2f getLimit() const;

  float getDistance() const;

  ::physx::PxJoint *getPxJoint() const override { return mJoint; }

  ~PhysxDistanceJointComponent();

private:
  ::physx::PxDistanceJoint *mJoint;
};

} // namespace physx
} // namespace sapien
