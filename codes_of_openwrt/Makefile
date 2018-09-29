include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

PKG_NAME:=sendudp
PKG_VERSION:=1
PKG_RELEASE:=1
PKG_LICENSE:=GPLv2+

include $(INCLUDE_DIR)/package.mk

define KernelPackage/sendudp
  SUBMENU:=Network Devices
  TITLE:=Send UDP in kernel
  # DEPENDS:= @(!(TARGET_ps3||TARGET_pxcab))
  DEPENDS:=+kmod-openvswitch +kmod-mac80211
  FILES:=$(PKG_BUILD_DIR)/sendudp.ko
  # AUTOLOAD:=$(call AutoProbe,sendudp)
endef

include $(INCLUDE_DIR)/kernel-defaults.mk

define KernelPackage/sendudp/description
  Send TCP info to a specific controller
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	cp src/* $(PKG_BUILD_DIR)/
endef

define Build/Compile
	$(MAKE) $(KERNEL_MAKEOPTS) SUBDIRS="$(PKG_BUILD_DIR)" modules
endef

$(eval $(call KernelPackage,sendudp))