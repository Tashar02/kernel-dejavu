%define _build_id_links none
%define _disable_source_fetch 0

# See https://fedoraproject.org/wiki/Changes/SetBuildFlagsBuildCheck to why this has to be done
%if 0%{?fedora} >= 37
%undefine _auto_set_build_flags
%endif

%ifarch x86_64
%define karch x86
%define asmarch x86
%endif

Name: kernel-dejavu
Summary: Custom Linux kernel tuned for performance

%define _basekver 6.1
%define _stablekver 3
Version: %{_basekver}.%{_stablekver}

%define krel 1

Release: %{krel}%{?dist}
Source0: %{name}-%{version}.tar.gz

%define rpmver %{version}-%{release}
%define kverstr %{version}-Dejavu%{release}.%{_arch}

License: GPLv2 and Redistributable, no modifications permitted
Group: System Environment/Kernel
Vendor: The Linux Community and dejavu maintainer(s)
URL: https://github.com/Neutron-Projects/kernel-dejavu
%define __spec_install_post /usr/lib/rpm/brp-compress || :
%define debug_package %{nil}
BuildRequires: python3-devel make perl-generators perl-interpreter openssl-devel bison flex findutils git-core perl-devel openssl elfutils-devel gawk binutils m4 tar hostname bzip2 bash gzip xz bc diffutils redhat-rpm-config net-tools elfutils patch rpm-build dwarves kmod libkcapi-hmaccalc perl-Carp rsync grubby
BuildRequires: wget zstd llvm lld clang
Requires: %{name}-core-%{rpmver} = %{kverstr}, %{name}-modules-%{rpmver} = %{kverstr}
Provides: %{name}%{_basekver} = %{rpmver}

%description
The kernel-dejavu meta package

%package core
Summary: Kernel core package
Group: System Environment/Kernel
Provides: installonlypkg(kernel), kernel = %{rpmver}, kernel-core = %{rpmver}, kernel-core-uname-r = %{kverstr}, kernel-uname-r = %{kverstr}, kernel-%{_arch} = %{rpmver}, kernel-core%{_isa} = %{rpmver}, kernel-core-%{rpmver} = %{kverstr}, %{name}-core-%{rpmver} = %{kverstr}, kernel-drm-nouveau = 16
# multiver
Provides: %{name}%{_basekver}-core = %{rpmver}
Requires: bash, coreutils, dracut, linux-firmware, /usr/bin/kernel-install, kernel-modules-%{rpmver} = %{kverstr}
Supplements: %{name} = %{rpmver}
%description core
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.

%package modules
Summary: Kernel modules to match the core kernel
Group: System Environment/Kernel
Provides: installonlypkg(kernel-module), kernel-modules = %{rpmver}, kernel-modules%{_isa} = %{rpmver}, kernel-modules-uname-r = %{kverstr}, kernel-modules-%{_arch} = %{rpmver}, kernel-modules-%{rpmver} = %{kverstr}, %{name}-modules-%{rpmver} = %{kverstr}
Provides: %{name}%{_basekver}-modules = %{rpmver}
Supplements: %{name} = %{rpmver}
%description modules
This package provides kernel modules for the core dejavu kernel package.

%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Provides: kernel-headers = %{kverstr}, glibc-kernheaders = 3.0-46, kernel-headers%{_isa} = %{kverstr}
Obsoletes: kernel-headers < %{kverstr}, glibc-kernheaders < 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package devel
Summary: Development package for building kernel modules to match the dejavu kernel
Group: System Environment/Kernel
AutoReqProv: no
Requires: findutils perl-interpreter openssl-devel flex make bison elfutils-libelf-devel
Requires: llvm lld clang wget zstd
Enhances: dkms akmods
Provides: installonlypkg(kernel), kernel-devel = %{rpmver}, kernel-devel-uname-r = %{kverstr}, kernel-devel-%{_arch} = %{rpmver}, kernel-devel%{_isa} = %{rpmver}, kernel-devel-%{rpmver} = %{kverstr}, %{name}-devel-%{rpmver} = %{kverstr}
Provides: %{name}%{_basekver}-devel = %{rpmver}
%description devel
This package provides kernel headers and makefiles sufficient to build modules
against the dejavu kernel package.

%package devel-matched
Summary: Meta package to install matching core and devel packages for a given dejavu kernel
Requires: %{name}-devel = %{rpmver}, %{name}-core = %{rpmver}
Provides: kernel-devel-matched = %{rpmver}, kernel-devel-matched%{_isa} = %{rpmver}
%description devel-matched
This meta package is used to install matching core and devel packages for a given dejavu kernel.

%prep
%setup -q
# Custom Clang toolchain
ls
cdir=$(pwd)
if test ! -d "$HOME/toolchains/neutron-clang"
then
  mkdir -p "$HOME/toolchains/neutron-clang"
  cd "$HOME/toolchains/neutron-clang"
  bash <(curl -s "https://raw.githubusercontent.com/Neutron-Toolchains/antman/main/antman") -S > /dev/null
fi
cd $cdir || cd -

export TC_PATH="$HOME/toolchains/neutron-clang/bin"
export PATH="$TC_PATH:$PATH"

# Verify clang version
clang --version
$TC_PATH/clang --version

export KBUILD_BUILD_USER="dakkshesh07"

# Init fedora_defconfig
make LLVM="$HOME/toolchains/neutron-clang/bin" LLVM_IAS=1 LD="$HOME/toolchains/neutron-clang/bin/ld.lld" fedora_defconfig

echo "kernel-str: %{kverstr}"
echo "local-version: -Dejavu%{release}.%{_arch}"

# Remove default localversion
find . -name "localversion*" -delete
scripts/config --set-str LOCALVERSION "-Dejavu%{release}.%{_arch}"

# Set kernel version string as build salt
scripts/config --set-str BUILD_SALT "%{kverstr}"

# Finalize the patched config
make LLVM=1 LLVM_IAS=1 CC="$TC_PATH/clang" LD="$TC_PATH/ld.lld" AR="$TC_PATH/llvm-ar" NM="$TC_PATH/llvm-nm" OBJCOPY="$TC_PATH/llvm-objcopy" OBJDUMP="$TC_PATH/llvm-objdump" READELF="$TC_PATH/llvm-readelf" STRIP="$TC_PATH/llvm-strip" HOSTCC="$TC_PATH/clang" HOSTCXX="$TC_PATH/clang++" HOSTAR="$TC_PATH/llvm-ar" HOSTLD="$TC_PATH/ld.lld" %{?_smp_mflags} oldconfig

%build
export TC_PATH="$HOME/toolchains/neutron-clang/bin"
export PATH="$TC_PATH:$PATH"

make LLVM=1 LLVM_IAS=1 CC="$TC_PATH/clang" LD="$TC_PATH/ld.lld" AR="$TC_PATH/llvm-ar" NM="$TC_PATH/llvm-nm" OBJCOPY="$TC_PATH/llvm-objcopy" OBJDUMP="$TC_PATH/llvm-objdump" READELF="$TC_PATH/llvm-readelf" STRIP="$TC_PATH/llvm-strip" HOSTCC="$TC_PATH/clang" HOSTCXX="$TC_PATH/clang++" HOSTAR="$TC_PATH/llvm-ar" HOSTLD="$TC_PATH/ld.lld" bzImage %{?_smp_mflags}
make LLVM=1 LLVM_IAS=1 CC="$TC_PATH/clang" LD="$TC_PATH/ld.lld" AR="$TC_PATH/llvm-ar" NM="$TC_PATH/llvm-nm" OBJCOPY="$TC_PATH/llvm-objcopy" OBJDUMP="$TC_PATH/llvm-objdump" READELF="$TC_PATH/llvm-readelf" STRIP="$TC_PATH/llvm-strip" HOSTCC="$TC_PATH/clang" HOSTCXX="$TC_PATH/clang++" HOSTAR="$TC_PATH/llvm-ar" HOSTLD="$TC_PATH/ld.lld" modules %{?_smp_mflags}
clang -O3 ./scripts/sign-file.c -o ./scripts/sign-file -lssl -lcrypto

%install
export TC_PATH="$HOME/toolchains/neutron-clang/bin"
export PATH="$TC_PATH:$PATH"

ImageName=$(make image_name | tail -n 1)

mkdir -p %{buildroot}/boot

cp -v $ImageName %{buildroot}/boot/vmlinuz-%{kverstr}
chmod 755 %{buildroot}/boot/vmlinuz-%{kverstr}

make %{?_smp_mflags} LLVM=1 LLVM_IAS=1 CC="$TC_PATH/clang" LD="$TC_PATH/ld.lld" AR="$TC_PATH/llvm-ar" NM="$TC_PATH/llvm-nm" OBJCOPY="$TC_PATH/llvm-objcopy" OBJDUMP="$TC_PATH/llvm-objdump" READELF="$TC_PATH/llvm-readelf" STRIP="$TC_PATH/llvm-strip" HOSTCC="$TC_PATH/clang" HOSTCXX="$TC_PATH/clang++" HOSTAR="$TC_PATH/llvm-ar" HOSTLD="$TC_PATH/ld.lld" INSTALL_MOD_PATH=%{buildroot} modules_install mod-fw=
make %{?_smp_mflags} LLVM=1 LLVM_IAS=1 CC="$TC_PATH/clang" LD="$TC_PATH/ld.lld" AR="$TC_PATH/llvm-ar" NM="$TC_PATH/llvm-nm" OBJCOPY="$TC_PATH/llvm-objcopy" OBJDUMP="$TC_PATH/llvm-objdump" READELF="$TC_PATH/llvm-readelf" STRIP="$TC_PATH/llvm-strip" HOSTCC="$TC_PATH/clang" HOSTCXX="$TC_PATH/clang++" HOSTAR="$TC_PATH/llvm-ar" HOSTLD="$TC_PATH/ld.lld" INSTALL_HDR_PATH=%{buildroot}/usr headers_install

# prepare -devel files
### all of the things here are derived from the Fedora kernel.spec
### see 
##### https://src.fedoraproject.org/rpms/kernel/blob/rawhide/f/kernel.spec
rm -f %{buildroot}/lib/modules/%{kverstr}/build
rm -f %{buildroot}/lib/modules/%{kverstr}/source
mkdir -p %{buildroot}/lib/modules/%{kverstr}/build
(cd %{buildroot}/lib/modules/%{kverstr} ; ln -s build source)
# dirs for additional modules per module-init-tools, kbuild/modules.txt
mkdir -p %{buildroot}/lib/modules/%{kverstr}/updates
mkdir -p %{buildroot}/lib/modules/%{kverstr}/weak-updates
# CONFIG_KERNEL_HEADER_TEST generates some extra files in the process of
# testing so just delete
find . -name *.h.s -delete
# first copy everything
cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` %{buildroot}/lib/modules/%{kverstr}/build
if [ ! -e Module.symvers ]; then
touch Module.symvers
fi
cp Module.symvers %{buildroot}/lib/modules/%{kverstr}/build
cp System.map %{buildroot}/lib/modules/%{kverstr}/build
if [ -s Module.markers ]; then
cp Module.markers %{buildroot}/lib/modules/%{kverstr}/build
fi
 
# create the kABI metadata for use in packaging
# NOTENOTE: the name symvers is used by the rpm backend
# NOTENOTE: to discover and run the /usr/lib/rpm/fileattrs/kabi.attr
# NOTENOTE: script which dynamically adds exported kernel symbol
# NOTENOTE: checksums to the rpm metadata provides list.
# NOTENOTE: if you change the symvers name, update the backend too
echo "**** GENERATING kernel ABI metadata ****"
gzip -c9 < Module.symvers > %{buildroot}/boot/symvers-%{kverstr}.gz
cp %{buildroot}/boot/symvers-%{kverstr}.gz %{buildroot}/lib/modules/%{kverstr}/symvers.gz

# then drop all but the needed Makefiles/Kconfig files
rm -rf %{buildroot}/lib/modules/%{kverstr}/build/scripts
rm -rf %{buildroot}/lib/modules/%{kverstr}/build/include
cp .config %{buildroot}/lib/modules/%{kverstr}/build
cp -a scripts %{buildroot}/lib/modules/%{kverstr}/build
rm -rf %{buildroot}/lib/modules/%{kverstr}/build/scripts/tracing
rm -f %{buildroot}/lib/modules/%{kverstr}/build/scripts/spdxcheck.py
 
%ifarch s390x
# CONFIG_EXPOLINE_EXTERN=y produces arch/s390/lib/expoline/expoline.o
# which is needed during external module build.
if [ -f arch/s390/lib/expoline/expoline.o ]; then
cp -a --parents arch/s390/lib/expoline/expoline.o %{buildroot}/lib/modules/%{kverstr}/build
fi
%endif
 
# Files for 'make scripts' to succeed with kernel-devel.
mkdir -p %{buildroot}/lib/modules/%{kverstr}/build/security/selinux/include
cp -a --parents security/selinux/include/classmap.h %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents security/selinux/include/initial_sid_to_string.h %{buildroot}/lib/modules/%{kverstr}/build
mkdir -p %{buildroot}/lib/modules/%{kverstr}/build/tools/include/tools
cp -a --parents tools/include/tools/be_byteshift.h %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/include/tools/le_byteshift.h %{buildroot}/lib/modules/%{kverstr}/build
 
# Files for 'make prepare' to succeed with kernel-devel.
cp -a --parents tools/include/linux/compiler* %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/include/linux/types.h %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/build/Build.include %{buildroot}/lib/modules/%{kverstr}/build
cp --parents tools/build/Build %{buildroot}/lib/modules/%{kverstr}/build
cp --parents tools/build/fixdep.c %{buildroot}/lib/modules/%{kverstr}/build
cp --parents tools/objtool/sync-check.sh %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/bpf/resolve_btfids %{buildroot}/lib/modules/%{kverstr}/build
 
cp --parents security/selinux/include/policycap_names.h %{buildroot}/lib/modules/%{kverstr}/build
cp --parents security/selinux/include/policycap.h %{buildroot}/lib/modules/%{kverstr}/build
 
cp -a --parents tools/include/asm-generic %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/include/linux %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/include/uapi/asm %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/include/uapi/asm-generic %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/include/uapi/linux %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/include/vdso %{buildroot}/lib/modules/%{kverstr}/build
cp --parents tools/scripts/utilities.mak %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/lib/subcmd %{buildroot}/lib/modules/%{kverstr}/build
cp --parents tools/lib/*.c %{buildroot}/lib/modules/%{kverstr}/build
cp --parents tools/objtool/*.[ch] %{buildroot}/lib/modules/%{kverstr}/build
cp --parents tools/objtool/Build %{buildroot}/lib/modules/%{kverstr}/build
cp --parents tools/objtool/include/objtool/*.h %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/lib/bpf %{buildroot}/lib/modules/%{kverstr}/build
cp --parents tools/lib/bpf/Build %{buildroot}/lib/modules/%{kverstr}/build

if [ -f tools/objtool/objtool ]; then
  cp -a tools/objtool/objtool %{buildroot}/lib/modules/%{kverstr}/build/tools/objtool/ || :
fi
if [ -f tools/objtool/fixdep ]; then
  cp -a tools/objtool/fixdep %{buildroot}/lib/modules/%{kverstr}/build/tools/objtool/ || :
fi
if [ -d arch/%{karch}/scripts ]; then
  cp -a arch/%{karch}/scripts %{buildroot}/lib/modules/%{kverstr}/build/arch/%{_arch} || :
fi
if [ -f arch/%{karch}/*lds ]; then
  cp -a arch/%{karch}/*lds %{buildroot}/lib/modules/%{kverstr}/build/arch/%{_arch}/ || :
fi
if [ -f arch/%{asmarch}/kernel/module.lds ]; then
  cp -a --parents arch/%{asmarch}/kernel/module.lds %{buildroot}/lib/modules/%{kverstr}/build/
fi
find %{buildroot}/lib/modules/%{kverstr}/build/scripts \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +
%ifarch ppc64le
cp -a --parents arch/powerpc/lib/crtsavres.[So] %{buildroot}/lib/modules/%{kverstr}/build/
%endif
if [ -d arch/%{asmarch}/include ]; then
  cp -a --parents arch/%{asmarch}/include %{buildroot}/lib/modules/%{kverstr}/build/
fi
%ifarch aarch64
# arch/arm64/include/asm/xen references arch/arm
cp -a --parents arch/arm/include/asm/xen %{buildroot}/lib/modules/%{kverstr}/build/
# arch/arm64/include/asm/opcodes.h references arch/arm
cp -a --parents arch/arm/include/asm/opcodes.h %{buildroot}/lib/modules/%{kverstr}/build/
%endif
# include the machine specific headers for ARM variants, if available.
%ifarch %{arm}
if [ -d arch/%{asmarch}/mach-${Variant}/include ]; then
  cp -a --parents arch/%{asmarch}/mach-${Variant}/include %{buildroot}/lib/modules/%{kverstr}/build/
fi
# include a few files for 'make prepare'
cp -a --parents arch/arm/tools/gen-mach-types %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/arm/tools/mach-types %{buildroot}/lib/modules/%{kverstr}/build/
 
%endif
cp -a include %{buildroot}/lib/modules/%{kverstr}/build/include

%ifarch i686 x86_64
# files for 'make prepare' to succeed with kernel-devel
cp -a --parents arch/x86/entry/syscalls/syscall_32.tbl %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/entry/syscalls/syscall_64.tbl %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/tools/relocs_32.c %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/tools/relocs_64.c %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/tools/relocs.c %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/tools/relocs_common.c %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/tools/relocs.h %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/purgatory/purgatory.c %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/purgatory/stack.S %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/purgatory/setup-x86_64.S %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/purgatory/entry64.S %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/boot/string.h %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/boot/string.c %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents arch/x86/boot/ctype.h %{buildroot}/lib/modules/%{kverstr}/build/
 
cp -a --parents scripts/syscalltbl.sh %{buildroot}/lib/modules/%{kverstr}/build/
cp -a --parents scripts/syscallhdr.sh %{buildroot}/lib/modules/%{kverstr}/build/
 
cp -a --parents tools/arch/x86/include/asm %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/arch/x86/include/uapi/asm %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/objtool/arch/x86/lib %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/arch/x86/lib/ %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/arch/x86/tools/gen-insn-attr-x86.awk %{buildroot}/lib/modules/%{kverstr}/build
cp -a --parents tools/objtool/arch/x86/ %{buildroot}/lib/modules/%{kverstr}/build
 
%endif
# Clean up intermediate tools files
find %{buildroot}/lib/modules/%{kverstr}/build/tools \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +
 
# Make sure the Makefile, version.h, and auto.conf have a matching
# timestamp so that external modules can be built
touch -r %{buildroot}/lib/modules/%{kverstr}/build/Makefile \
%{buildroot}/lib/modules/%{kverstr}/build/include/generated/uapi/linux/version.h \
%{buildroot}/lib/modules/%{kverstr}/build/include/config/auto.conf

find %{buildroot}/lib/modules/%{kverstr} -name "*.ko" -type f >modnames
 
# mark modules executable so that strip-to-file can strip them
xargs --no-run-if-empty chmod u+x < modnames
 
# Generate a list of modules for block and networking.
 
grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef
 
collect_modules_list()
{
  sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
LC_ALL=C sort -u > %{buildroot}/lib/modules/%{kverstr}/modules.$1
  if [ ! -z "$3" ]; then
sed -r -e "/^($3)\$/d" -i %{buildroot}/lib/modules/%{kverstr}/modules.$1
  fi
}
 
collect_modules_list networking \
  'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt(l_|2x00)(pci|usb)_probe|register_netdevice'
collect_modules_list block \
  'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' 'pktcdvd.ko|dm-mod.ko'
collect_modules_list drm \
  'drm_open|drm_init'
collect_modules_list modesetting \
  'drm_crtc_init'
 
# detect missing or incorrect license tags
( find %{buildroot}/lib/modules/%{kverstr} -name '*.ko' | xargs /sbin/modinfo -l | \
grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' ) && exit 1
 
remove_depmod_files()
{
# remove files that will be auto generated by depmod at rpm -i time
pushd %{buildroot}/lib/modules/%{kverstr}/
rm -f modules.{alias,alias.bin,builtin.alias.bin,builtin.bin} \
  modules.{dep,dep.bin,devname,softdep,symbols,symbols.bin}
popd
}
 
remove_depmod_files

mkdir -p %{buildroot}%{_prefix}/src/kernels
mv %{buildroot}/lib/modules/%{kverstr}/build %{buildroot}%{_prefix}/src/kernels/%{kverstr}
 
# This is going to create a broken link during the build, but we don't use
# it after this point.  We need the link to actually point to something
# when kernel-devel is installed, and a relative link doesn't work across
# the F17 UsrMove feature.
ln -sf %{_prefix}/src/kernels/%{kverstr} %{buildroot}/lib/modules/%{kverstr}/build
  
find %{buildroot}%{_prefix}/src/kernels -name ".*.cmd" -delete
#

cp -v System.map %{buildroot}/boot/System.map-%{kverstr}
cp -v System.map %{buildroot}/lib/modules/%{kverstr}/System.map
cp -v .config %{buildroot}/boot/config-%{kverstr}
cp -v .config %{buildroot}/lib/modules/%{kverstr}/config

(cd "%{buildroot}/boot/" && sha512hmac "vmlinuz-%{kverstr}" > ".vmlinuz-%{kverstr}.hmac")

cp -v  %{buildroot}/boot/vmlinuz-%{kverstr} %{buildroot}/lib/modules/%{kverstr}/vmlinuz
(cd "%{buildroot}/lib/modules/%{kverstr}" && sha512hmac vmlinuz > .vmlinuz.hmac)

# create dummy initramfs image to inflate the disk space requirement for the initramfs. 48M seems to be the right size nowadays with more and more hardware requiring initramfs-located firmware to work properly (for reference, Fedora has it set to 20M)
dd if=/dev/zero of=%{buildroot}/boot/initramfs-%{kverstr}.img bs=1M count=48

%clean
rm -rf %{buildroot}

%post core
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ] &&
   [ -f /etc/sysconfig/kernel ]; then
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=kernel-smp$/DEFAULTKERNEL=kernel/' /etc/sysconfig/kernel || exit $?
fi

%posttrans core
/bin/kernel-install add %{kverstr} /lib/modules/%{kverstr}/vmlinuz || exit $?

%preun core
/bin/kernel-install remove %{kverstr} /lib/modules/%{kverstr}/vmlinuz || exit $?
if [ -x /usr/sbin/weak-modules ]
then
/usr/sbin/weak-modules --remove-kernel %{kverstr} || exit $?
fi

%post devel
if [ -f /etc/sysconfig/kernel ]
then
. /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/bin/hardlink -a ! -e /run/ostree-booted ] 
then
(cd /usr/src/kernels/%{kverstr} &&
 /usr/bin/find . -type f | while read f; do
   hardlink -c /usr/src/kernels/*%{?dist}.*/$f $f 2>&1 >/dev/null
 done)
fi

%post modules
/sbin/depmod -a %{kverstr}

%postun modules
/sbin/depmod -a %{kverstr}

%files core
%ghost %attr(0600, root, root) /boot/vmlinuz-%{kverstr}
%ghost %attr(0600, root, root) /boot/System.map-%{kverstr}
%ghost %attr(0600, root, root) /boot/initramfs-%{kverstr}.img
%ghost %attr(0600, root, root) /boot/symvers-%{kverstr}.gz
%ghost %attr(0644, root, root) /boot/config-%{kverstr}
/boot/.vmlinuz-%{kverstr}.hmac
%dir /lib/modules/%{kverstr}
%dir /lib/modules/%{kverstr}/kernel
/lib/modules/%{kverstr}/.vmlinuz.hmac
/lib/modules/%{kverstr}/config
/lib/modules/%{kverstr}/vmlinuz
/lib/modules/%{kverstr}/System.map
/lib/modules/%{kverstr}/symvers.gz

%files modules
%defattr (-, root, root)
/lib/modules/%{kverstr}/*
%exclude /lib/modules/%{kverstr}/.vmlinuz.hmac
%exclude /lib/modules/%{kverstr}/config
%exclude /lib/modules/%{kverstr}/vmlinuz
%exclude /lib/modules/%{kverstr}/System.map
%exclude /lib/modules/%{kverstr}/symvers.gz
%exclude /lib/modules/%{kverstr}/build
%exclude /lib/modules/%{kverstr}/source

%files headers
%defattr (-, root, root)
/usr/include/*

%files devel
%defattr (-, root, root)
/usr/src/kernels/%{kverstr}
/lib/modules/%{kverstr}/build
/lib/modules/%{kverstr}/source

%files devel-matched

%files

%changelog
* Sun Jan 01 2023 Dakkshesh <dakkshesh5@gmail.com> 6.1.2-1
- dejavu: 6.1.2-1 (dakkshesh5@gmail.com)
- sched: Introduce per-memory-map concurrency ID (admin@ptr1337.dev)
- Revert "Add latency priority for CFS class" (dakkshesh5@gmail.com)
- spec: Fix TC_PATH for %%build and %%install (dakkshesh5@gmail.com)
- spec: set KBUILD_BUILD_USER (dakkshesh5@gmail.com)
- scripts/mkcompile_h: Trim URL from custom compiler (cyberknight755@gmail.com)
- spec: Explicitly pass toolchain path to make variables (dakkshesh5@gmail.com)
- x86/configs: fedora: Regenerate for toolchain update (dakkshesh5@gmail.com)
- Makefile: Switch to O3 for HOST flags (dakkshesh5@gmail.com)
- xfs: Fix deadlock on xfs_inodegc_worker (wuguanghao3@huawei.com)
- xfs: get root inode correctly at bulkstat (shiina.hironori@gmail.com)
- xfs: fix off-by-one error in xfs_btree_space_to_height (djwong@kernel.org)
- xfs: make xfs_iomap_page_ops static (djwong@kernel.org)
- xfs: don't assert if cmap covers imap after cycling lock (djwong@kernel.org)
- XANMOD: cpufreq: tunes ondemand and conservative governor for performance
  (admfrade@gmail.com)
- XANMOD: dcache: cache_pressure = 50 decreases the rate at which VFS caches
  are reclaimed (admfrade@gmail.com)
- block: Do not collect I/O statistics (tylernij@gmail.com)
- sched: Increase the time a task is considered cache-hot (tylernij@gmail.com)
- x86/configs: fedora: Regenerate (dakkshesh5@gmail.com)
- zsmalloc: Implement writeback mechanism for zsmalloc (nphamcs@gmail.com)
- zsmalloc: Add zpool_ops field to zs_pool to store evict handlers
  (nphamcs@gmail.com)
- zsmalloc: Add a LRU to zs_pool to keep track of zspages in LRU order
  (nphamcs@gmail.com)
- zsmalloc: Consolidate zs_pool's migrate_lock and size_class's locks
  (nphamcs@gmail.com)
- zpool: clean out dead code (hannes@cmpxchg.org)
- zswap: fix writeback lock ordering for zsmalloc (hannes@cmpxchg.org)
- module/decompress: Support zstd in-kernel decompression (swboyd@chromium.org)
- kbuild-modules-6.1: allow setting zstd compression level for modules and the
  kernel image (lucjan.lucjanov@gmail.com)
- zstd/decompress: fix repeated words in comments (wangjianli@cdjrlc.com)
- zstd/compress: fix repeated words in comments (wangjianli@cdjrlc.com)
- zstd/common: fix repeated words in comments (wangjianli@cdjrlc.com)
- zstd: import usptream v1.5.2 (terrelln@fb.com)
- zstd: Move zstd-common module exports to zstd_common_module.c
  (terrelln@fb.com)
- lib: zstd: Fix comment typo (gaoxin@cdjrlc.com)
- MAINTAINERS: git://github -> https://github.com for terrelln
  (palmer@rivosinc.com)
- i2c: i2c-nct6775: fix -Wimplicit-fallthrough (alobakin@pm.me)
- ZEN: intel-pstate: Implement "enable" parameter (steven@liquorix.net)
- ZEN: cpufreq: Remove schedutil dependency on Intel/AMD P-State drivers
  (steven@liquorix.net)
- ZEN: PCI: Add Intel remapped NVMe device support (drake@endlessm.com)
- ZEN: Add OpenRGB patches (heftig@archlinux.org)
- zram-6.1: Introduce merge identical pages mechanism
  (lucjan.lucjanov@gmail.com)
- zram-6.1: Support multiple compression streams (lucjan.lucjanov@gmail.com)
- compiler: Always inline (kazukih@tuta.io)
- Revert "kbuild: lto: limit inlining" (me@const.eu.org)
- ata: libahci: ignore staggered spin-up (joe.konno@intel.com)
- rcu: Make the grace period workers unbound again (sultan@kerneltoast.com)
- mm: delay page_remove_rmap() until after the TLB has been flushed
  (torvalds@linux-foundation.org)
- mm: mmu_gather: prepare to gather encoded page pointers with flags
  (torvalds@linux-foundation.org)
- mm: teach release_pages() to take an array of encoded page pointers too
  (torvalds@linux-foundation.org)
- mm: introduce 'encoded' page pointers with embedded extra bits
  (torvalds@linux-foundation.org)
- mm, slob: rename CONFIG_SLOB to CONFIG_SLOB_DEPRECATED (vbabka@suse.cz)
- mm, slub: don't aggressively inline with CONFIG_SLUB_TINY (vbabka@suse.cz)
- mm, slub: remove percpu slabs with CONFIG_SLUB_TINY (vbabka@suse.cz)
- mm, slub: split out allocations from pre/post hooks (vbabka@suse.cz)
- mm, slub: refactor free debug processing (vbabka@suse.cz)
- mm, slab: ignore SLAB_RECLAIM_ACCOUNT with CONFIG_SLUB_TINY (vbabka@suse.cz)
- mm, slub: don't create kmalloc-rcl caches with CONFIG_SLUB_TINY
  (vbabka@suse.cz)
- mm, slub: lower the default slub_max_order with CONFIG_SLUB_TINY
  (vbabka@suse.cz)
- mm, slub: retain no free slabs on partial list with CONFIG_SLUB_TINY
  (vbabka@suse.cz)
- mm, slub: disable SYSFS support with CONFIG_SLUB_TINY (vbabka@suse.cz)
- mm, slub: add CONFIG_SLUB_TINY (vbabka@suse.cz)
- mm, slab: ignore hardened usercopy parameters when disabled (vbabka@suse.cz)
- mm: introduce THP Shrinker (lucjan.lucjanov@gmail.com)
- Tune mgLRU to protect cache used in the last second
  (lucjan.lucjanov@gmail.com)
- maple_tree: refine mab_calc_split function (vernon2gm@gmail.com)
- maple_tree: refine ma_state init from mas_start() (vernon2gm@gmail.com)
- maple_tree: remove the redundant code (vernon2gm@gmail.com)
- maple_tree: use macro MA_ROOT_PARENT instead of number (vernon2gm@gmail.com)
- maple_tree: use mt_node_max() instead of direct operations mt_max[]
  (vernon2gm@gmail.com)
- maple_tree: remove extra return statement (vernon2gm@gmail.com)
- maple_tree: remove extra space and blank line (vernon2gm@gmail.com)
- mm: multi-gen LRU: simplify arch_has_hw_pte_young() check (yuzhao@google.com)
- mm: multi-gen LRU: clarify scan_control flags (yuzhao@google.com)
- mm: multi-gen LRU: per-node lru_gen_folio lists (yuzhao@google.com)
- mm: multi-gen LRU: shuffle should_run_aging() (yuzhao@google.com)
- mm: multi-gen LRU: remove aging fairness safeguard (yuzhao@google.com)
- mm: multi-gen LRU: remove eviction fairness safeguard (yuzhao@google.com)
- mm: multi-gen LRU: rename lrugen->lists[] to lrugen->folios[]
  (yuzhao@google.com)
- mm: multi-gen LRU: rename lru_gen_struct to lru_gen_folio (yuzhao@google.com)
- mm: multi-gen LRU: remove NULL checks on NODE_DATA() (yuzhao@google.com)
- maple_tree: not necessary to filter MAPLE_PARENT_ROOT since it is not a root
  (richard.weiyang@gmail.com)
- maple_tree: should get pivots boundary by type (richard.weiyang@gmail.com)
- mm/demotion: Fix NULL vs IS_ERR checking in memory_tier_init
  (linmq006@gmail.com)
- maple_tree: mte_set_full() and mte_clear_full() clang-analyzer clean up
  (liam.howlett@oracle.com)
- ZENIFY: Tune CFS for interactivity (jan.steffens@gmail.com)
- zsmalloc: add bp hints to memory allocations (qkrwngud825@gmail.com)
- kernel: Allow wakeup IRQs to cancel ongoing suspend (sultan@kerneltoast.com)
- PM / freezer: Abort suspend when there's a wakeup while freezing
  (sultan@kerneltoast.com)
- PM / suspend: Clear wakeups before running PM callbacks
  (sultan@kerneltoast.com)
- PM / wakeup: Avoid excessive s2idle wake attempts in pm_system_wakeup()
  (sultan@kerneltoast.com)
- timekeeping: Keep the tick alive when CPUs cycle out of s2idle
  (sultan@kerneltoast.com)
- rcu/kfree: Do not request RCU when not needed (joel@joelfernandes.org)
- fs/ntfs3: Make if more readable (almaz.alexandrovich@paragon-software.com)
- fs/ntfs3: Improve checking of bad clusters (almaz.alexandrovich@paragon-
  software.com)
- fs/ntfs3: Fix wrong if in hdr_first_de (almaz.alexandrovich@paragon-
  software.com)
- fs/ntfs3: Use ALIGN kernel macro (almaz.alexandrovich@paragon-software.com)
- fs/ntfs3: Fix incorrect if in ntfs_set_acl_ex (almaz.alexandrovich@paragon-
  software.com)
- fs/ntfs3: Check fields while reading (almaz.alexandrovich@paragon-
  software.com)
- fs/ntfs3: Correct ntfs_check_for_free_space (almaz.alexandrovich@paragon-
  software.com)
- fs/ntfs3: Restore correct state after ENOSPC in attr_data_get_block
  (almaz.alexandrovich@paragon-software.com)
- fs/ntfs3: Changing locking in ntfs_rename (almaz.alexandrovich@paragon-
  software.com)
- fs/ntfs3: Fixing wrong logic in attr_set_size and ntfs_fallocate
  (almaz.alexandrovich@paragon-software.com)
- fs/ntfs3: atomic_open implementation (almaz.alexandrovich@paragon-
  software.com)
- fs/ntfs3: Fix wrong indentations (almaz.alexandrovich@paragon-software.com)
- fs/ntfs3: Change new sparse cluster processing (almaz.alexandrovich@paragon-
  software.com)
- fs/ntfs3: Fixing work with sparse clusters (almaz.alexandrovich@paragon-
  software.com)
- fs/ntfs3: Simplify ntfs_update_mftmirr function (almaz.alexandrovich@paragon-
  software.com)
- fs/ntfs3: Remove unused functions (almaz.alexandrovich@paragon-software.com)
- fs/ntfs3: Fix sparse problems (almaz.alexandrovich@paragon-software.com)
- fs/ntfs3: Add ntfs_bitmap_weight_le function and refactoring
  (almaz.alexandrovich@paragon-software.com)
- fs/ntfs3: Use _le variants of bitops functions (thomas.kuehnel@avm.de)
- fs/ntfs3: Add functions to modify LE bitmaps (thomas.kuehnel@avm.de)
- fs/ntfs3: Fix endian conversion in ni_fname_name (thomas.kuehnel@avm.de)
- fs/ntfs3: Fix slab-out-of-bounds in r_page (yinxiujiang@kylinos.cn)
- fs/ntfs3: Delete duplicate condition in ntfs_read_mft()
  (dan.carpenter@oracle.com)
- fs/ntfs3: Document system.ntfs_attrib_be extended attribute
  (danielpinto52@gmail.com)
- fs/ntfs3: Add system.ntfs_attrib_be extended attribute
  (danielpinto52@gmail.com)
- fs/ntfs3: Rename hidedotfiles mount option to hide_dot_files
  (danielpinto52@gmail.com)
- fs/ntfs3: Document the hidedotfiles mount option (danielpinto52@gmail.com)
- fs/ntfs3: Add hidedotfiles to the list of enabled mount options
  (danielpinto52@gmail.com)
- fs/ntfs3: Make hidedotfiles mount option work when renaming files
  (danielpinto52@gmail.com)
- fs/ntfs3: Fix hidedotfiles mount option by reversing behaviour
  (danielpinto52@gmail.com)
- fs/ntfs3: Document windows_names mount option (danielpinto52@gmail.com)
- fs/ntfs3: Add windows_names mount option (danielpinto52@gmail.com)
- fs/ntfs3: Eliminate unnecessary ternary operator in ntfs_d_compare()
  (nathan@kernel.org)
- fs/ntfs3: Validate attribute data and valid sizes (abdun.nihaal@gmail.com)
- fs/ntfs3: Use __GFP_NOWARN allocation at ntfs_fill_super() (penguin-
  kernel@I-love.SAKURA.ne.jp)
- fs/ntfs3: Use __GFP_NOWARN allocation at wnd_init() (penguin-
  kernel@I-love.SAKURA.ne.jp)
- fs/ntfs3: Validate index root when initialize NTFS security
  (edward.lo@ambergroup.io)
- fs/ntfs3: Don't use uni1 uninitialized in ntfs_d_compare()
  (nathan@kernel.org)
- fs/ntfs3: Use strcmp to determine attribute type (yuancan@huawei.com)
- fs/ntfs3: Fix slab-out-of-bounds read in run_unpack (yin31149@gmail.com)
- fs/ntfs3: Validate resident attribute name (edward.lo@ambergroup.io)
- fs/ntfs3: Validate buffer length while parsing index
  (edward.lo@ambergroup.io)
- fs/ntfs3: Validate attribute name offset (edward.lo@ambergroup.io)
- fs/ntfs3: Add null pointer check for inode operations
  (edward.lo@ambergroup.io)
- fs/ntfs3: Fix junction point resolution (danielpinto52@gmail.com)
- fs/ntfs3: Fix memory leak on ntfs_fill_super() error path
  (syoshida@redhat.com)
- fs/ntfs3: Use kmalloc_array for allocating multiple elements (klee33@uw.edu)
- fs/ntfs3: Fix attr_punch_hole() null pointer derenference
  (zahavi.alon@gmail.com)
- fs/ntfs3: Fix [df]mask display in /proc/mounts (tsi@tuyoix.net)
- fs/ntfs3: Add null pointer check to attr_load_runs_vcn
  (edward.lo@ambergroup.io)
- Revert "ntfs3: rework xattr handlers and switch to POSIX ACL VFS helpers"
  (me@const.eu.org)
- fs/ntfs3: Validate data run offset (edward.lo@ambergroup.io)
- fs/ntfs3: Add overflow check for attribute size (edward.lo@ambergroup.io)
- fs/ntfs3: Validate BOOT record_size (edward.lo@ambergroup.io)
- fs/ntfs3: Rename variables and add comment (almaz.alexandrovich@paragon-
  software.com)
- fs/ntfs3: Add option "nocase" (almaz.alexandrovich@paragon-software.com)
- fs/ntfs3: Change destroy_inode to free_inode (almaz.alexandrovich@paragon-
  software.com)
- fs/ntfs3: Add hidedotfiles option (almaz.alexandrovich@paragon-software.com)
- fs/ntfs3: Add comments about cluster size (almaz.alexandrovich@paragon-
  software.com)
- Add latency priority for CFS class (admin@ptr1337.dev)
- tracing/rseq: Add mm_cid field to rseq_update
  (mathieu.desnoyers@efficios.com)
- rseq: Extend struct rseq with per-memory-map concurrency ID
  (mathieu.desnoyers@efficios.com)
- rseq: Extend struct rseq with numa node id (mathieu.desnoyers@efficios.com)
- rseq: Introduce extensible rseq ABI (mathieu.desnoyers@efficios.com)
- rseq: Introduce feature size and alignment ELF auxiliary vector entries
  (mathieu.desnoyers@efficios.com)
- sched/core: Adjusting the order of scanning CPU (jiahao.os@bytedance.com)
- sched/numa: Stop an exhastive search if an idle core is found
  (jiahao.os@bytedance.com)
- sched: Make const-safe (willy@infradead.org)
- sched: Async unthrottling for cfs bandwidth (joshdon@google.com)
- sched: Clear ttwu_pending after enqueue_task() (dtcccc@linux.alibaba.com)
- sched/psi: Use task->psi_flags to clear in CPU migration
  (zhouchengming@bytedance.com)
- sched/psi: Stop relying on timer_pending() for poll_work rescheduling
  (surenb@google.com)
- sched/psi: Fix avgs_work re-arm in psi_avgs_work()
  (zhouchengming@bytedance.com)
- sched: Always clear user_cpus_ptr in do_set_cpus_allowed()
  (longman@redhat.com)
- sched: Enforce user requested affinity (longman@redhat.com)
- sched: Always preserve the user requested cpumask (longman@redhat.com)
- sched: Introduce affinity_context (longman@redhat.com)
- bfq (admin@ptr1337.dev)
- Input: evdev - use call_rcu when detaching client (kl@kl.wtf)
- x86/configs: fedora: Regenerate (dakkshesh5@gmail.com)
- x86: Inline the spin lock function family (sultan@kerneltoast.com)
- sched/fair: Compile out NUMA code entirely when NUMA is disabled
  (sultan@kerneltoast.com)
- x86/split_lock: turn off by default (Jason@zx2c4.com)
- thread_info: Order thread flag tests with respect to flag mutations
  (sultan@kerneltoast.com)
- kbuild: Disable stack conservation for GCC (sultan@kerneltoast.com)
- x86/mce/therm_throt: allow disabling the thermal vector altogether
  (Jason@zx2c4.com)
- x86/mce/therm_throt: allow disabling verbose logging (Jason@zx2c4.com)
- x86/mce/therm_throt: remove unused platform_thermal_notify function pointer
  (Jason@zx2c4.com)
- mm: Increment kswapd_waiters for throttled direct reclaimers
  (sultan@kerneltoast.com)
- mm: Don't stop kswapd on a per-node basis when there are no waiters
  (sultan@kerneltoast.com)
- mm: bump DEFAULT_MAX_MAP_COUNT (ti3nou@gmail.com)
- Set vm.max_map_count to 262144 by default (ti3nou@gmail.com)
- crypto: x86/ghash - add comment and fix broken link (ebiggers@google.com)
- crypto: x86/ghash - use le128 instead of u128 (ebiggers@google.com)
- crypto: x86/ghash - fix unaligned access in ghash_setkey()
  (ebiggers@google.com)
- kbuild: pass jobserver to cmd_ld_vmlinux.o (jslaby@suse.cz)
- x86/boot: robustify calling startup_{32,64}() from the decompressor code
  (alexandr.lobakin@intel.com)
- ALSA: hda/hdmi: Static PCM mapping again with AMD HDMI codecs (tiwai@suse.de)
- rtmutex: Add acquire semantics for rtmutex lock acquisition slow path
  (mgorman@techsingularity.net)
- hugetlb: really allocate vma lock for all sharable vmas
  (mike.kravetz@oracle.com)
- mm, mremap: fix mremap() expanding vma with addr inside vma (vbabka@suse.cz)
- epoll: ep_autoremove_wake_function should use list_del_init_careful
  (bsegall@google.com)
- kbuild: revive parallel execution for .tmp_initcalls.lds rule
  (masahiroy@kernel.org)
- objtool: Optimize elf_dirty_reloc_sym() (peterz@infradead.org)
- mm: vmscan: make rotations a secondary factor in balancing anon vs file
  (hannes@cmpxchg.org)
- blk-wbt: don't enable throttling if default elevator is bfq
  (yukuai3@huawei.com)
- elevator: add new field flags in struct elevator_queue (yukuai3@huawei.com)
- blk-wbt: don't show valid wbt_lat_usec in sysfs while wbt is disabled
  (yukuai3@huawei.com)
- blk-wbt: make enable_state more accurate (yukuai3@huawei.com)
- blk-wbt: remove unnecessary check in wbt_enable_default()
  (yukuai3@huawei.com)
- elevator: remove redundant code in elv_unregister_queue()
  (yukuai3@huawei.com)
- padata: Do not mark padata_mt_helper() as __init (nathan@kernel.org)
- clearlinux-6.1: introduce clearlinux patchset (lucjan.lucjanov@gmail.com)
- lib/cpumask: update comment for cpumask_local_spread() (yury.norov@gmail.com)
- net/mlx5e: Improve remote NUMA preferences used for the IRQ affinity hints
  (tariqt@nvidia.com)
- sched/topology: Introduce for_each_numa_hop_mask() (vschneid@redhat.com)
- sched/topology: Introduce sched_numa_hop_mask() (vschneid@redhat.com)
- lib/cpumask: reorganize cpumask_local_spread() logic (yury.norov@gmail.com)
- cpumask: improve on cpumask_local_spread() locality (yury.norov@gmail.com)
- sched: add sched_numa_find_nth_cpu() (yury.norov@gmail.com)
- cpumask: introduce cpumask_nth_and_andnot (yury.norov@gmail.com)
- lib/find: introduce find_nth_and_andnot_bit (yury.norov@gmail.com)
- bitmap: add tests for find_next_bit() (yury.norov@gmail.com)
- bitmap: improve small_const case for find_next() functions
  (yury.norov@gmail.com)
- bitmap: switch from inline to __always_inline (yury.norov@gmail.com)
- mm: Change dirty writeback defaults (torvic9@mailbox.org)
- futex: Fix futex_waitv() hrtimer debug object leak on kcalloc error
  (admin@ptr1337.dev)
- fixdep: remove unneeded <stdarg.h> inclusion (masahiroy@kernel.org)
- kbuild: sort single-targets alphabetically again (masahiroy@kernel.org)
- kbuild: rpm-pkg: add libelf-devel as alternative for BuildRequires
  (masahiroy@kernel.org)
- kbuild: Fix running modpost with musl libc (samuel@sholland.org)
- kbuild: add a missing line for help message (JunASAKA@zzy040330.moe)
- .gitignore: ignore *.rpm (masahiroy@kernel.org)
- arch: fix broken BuildID for arm64 and riscv (masahiroy@kernel.org)
- kconfig: Add static text for search information in help menu
  (unixbhaskar@gmail.com)
- Linux 6.1.2 (gregkh@linuxfoundation.org)
- pwm: tegra: Fix 32 bit build (steven.price@arm.com)
- mfd: qcom_rpm: Use devm_of_platform_populate() to simplify code
  (christophe.jaillet@wanadoo.fr)
- drm/amd/display: revert Disable DRR actions during state commit
  (Martin.Leung@amd.com)
- media: dvbdev: fix refcnt bug (linma@zju.edu.cn)
- media: dvbdev: fix build warning due to comments (linma@zju.edu.cn)
- net: stmmac: fix errno when create_singlethread_workqueue() fails
  (cuigaosheng1@huawei.com)
- io_uring: remove iopoll spinlock (asml.silence@gmail.com)
- io_uring: protect cq_timeouts with timeout_lock (asml.silence@gmail.com)
- io_uring/net: fix cleanup after recycle (asml.silence@gmail.com)
- io_uring/net: ensure compat import handlers clear free_iov (axboe@kernel.dk)
- io_uring: improve io_double_lock_ctx fail handling (asml.silence@gmail.com)
- io_uring: dont remove file from msg_ring reqs (asml.silence@gmail.com)
- io_uring: add completion locking for iopoll (asml.silence@gmail.com)
- io_uring/net: introduce IORING_SEND_ZC_REPORT_USAGE flag (metze@samba.org)
- blk-iolatency: Fix memory leak on add_disk() failures (tj@kernel.org)
- scsi: qla2xxx: Fix crash when I/O abort times out (aeasi@marvell.com)
- mm/gup: disallow FOLL_FORCE|FOLL_WRITE on hugetlb mappings (david@redhat.com)
- btrfs: do not BUG_ON() on ENOMEM when dropping extent items for a range
  (fdmanana@suse.com)
- ovl: fix use inode directly in rcu-walk mode (chenzhongjin@huawei.com)
- fbdev: fbcon: release buffer when fbcon_do_set_font() failed (penguin-
  kernel@I-love.SAKURA.ne.jp)
- maple_tree: fix mas_spanning_rebalance() on insufficient data
  (liam.howlett@oracle.com)
- test_maple_tree: add test for mas_spanning_rebalance() on insufficient data
  (liam.howlett@oracle.com)
- gcov: add support for checksum field (rickaran@axis.com)
- floppy: Fix memory leak in do_floppy_init() (yuancan@huawei.com)
- spi: fsl_spi: Don't change speed while chipselect is active
  (christophe.leroy@csgroup.eu)
- regulator: core: fix deadlock on regulator enable (johan+linaro@kernel.org)
- iio: addac: ad74413r: fix integer promotion bug in
  ad74413_get_input_current_offset() (linux@rasmusvillemoes.dk)
- iio: adc128s052: add proper .data members in adc128_of_match table
  (linux@rasmusvillemoes.dk)
- iio: adc: ad_sigma_delta: do not use internal iio_dev lock
  (nuno.sa@analog.com)
- iio: fix memory leak in iio_device_register_eventset() (zengheng4@huawei.com)
- reiserfs: Add missing calls to reiserfs_security_free()
  (roberto.sassu@huawei.com)
- security: Restrict CONFIG_ZERO_CALL_USED_REGS to gcc or clang > 15.0.6
  (nathan@kernel.org)
- 9p: set req refcount to zero to avoid uninitialized usage (schspa@gmail.com)
- loop: Fix the max_loop commandline argument treatment when it is set to 0
  (isaacmanjarres@google.com)
- HID: mcp2221: don't connect hidraw (Enrik.Berkhan@inka.de)
- HID: wacom: Ensure bootloader PID is usable in hidraw mode
  (killertofu@gmail.com)
- xhci: Prevent infinite loop in transaction errors recovery for streams
  (mathias.nyman@linux.intel.com)
- usb: dwc3: qcom: Fix memory leak in dwc3_qcom_interconnect_init
  (linmq006@gmail.com)
- usb: dwc3: core: defer probe on ulpi_read_id timeout (ftoth@exalondelft.nl)
- usb: dwc3: Fix race between dwc3_set_mode and __dwc3_set_mode
  (sven@svenpeter.dev)
- clk: imx: imx8mp: add shared clk gate for usb suspend clk (jun.li@nxp.com)
- dt-bindings: clocks: imx8mp: Add ID for usb suspend clock (jun.li@nxp.com)
- arm64: dts: qcom: sm8250: fix USB-DP PHY registers (johan+linaro@kernel.org)
- arm64: dts: qcom: sm6350: fix USB-DP PHY registers (johan+linaro@kernel.org)
- usb: xhci-mtk: fix leakage of shared hcd when fail to set wakeup irq
  (chunfeng.yun@mediatek.com)
- usb: cdnsp: fix lack of ZLP for ep0 (pawell@cadence.com)
- HID: logitech-hidpp: Guard FF init code against non-USB devices
  (hadess@hadess.net)
- ALSA: hda/hdmi: Add HP Device 0x8711 to force connect list
  (jiaozhou@google.com)
- ALSA: hda/realtek: Add quirk for Lenovo TianYi510Pro-14IOB
  (edward@edward-p.xyz)
- ALSA: usb-audio: add the quirk for KT0206 device (wangdicheng@kylinos.cn)
- ALSA: usb-audio: Workaround for XRUN at prepare (tiwai@suse.de)
- dt-bindings: input: iqs7222: Add support for IQS7222A v1.13+
  (jeff@labundy.com)
- dt-bindings: input: iqs7222: Correct minimum slider size (jeff@labundy.com)
- dt-bindings: input: iqs7222: Reduce 'linux,code' to optional
  (jeff@labundy.com)
- Input: iqs7222 - add support for IQS7222A v1.13+ (jeff@labundy.com)
- Input: iqs7222 - report malformed properties (jeff@labundy.com)
- Input: iqs7222 - drop unused device node references (jeff@labundy.com)
- ima: Simplify ima_lsm_copy_rule (guozihua@huawei.com)
- pstore: Make sure CONFIG_PSTORE_PMSG selects CONFIG_RT_MUTEXES
  (jstultz@google.com)
- cfi: Fix CFI failure with KASAN (samitolvanen@google.com)
- afs: Fix lost servers_outstanding count (dhowells@redhat.com)
- perf test: Fix "all PMU test" to skip parametrized events
  (mpetlan@redhat.com)
- MIPS: ralink: mt7621: avoid to init common ralink reset controller
  (sergio.paracuellos@gmail.com)
- perf probe: Check -v and -q options in the right place
  (yangjihong1@huawei.com)
- perf tools: Make quiet mode consistent between tools (james.clark@arm.com)
- perf debug: Set debug_peo_args and redirect_to_stderr variable to correct
  values in perf_quiet_option() (yangjihong1@huawei.com)
- drm/amd/pm: avoid large variable on kernel stack (arnd@arndb.de)
- pstore: Switch pmsg_lock to an rt_mutex to avoid priority inversion
  (jstultz@google.com)
- lkdtm: cfi: Make PAC test work with GCC 7 and 8 (kristina.martsenko@arm.com)
- LoadPin: Ignore the "contents" argument of the LSM hooks
  (keescook@chromium.org)
- drm/i915/display: Don't disable DDI/Transcoder when setting phy test pattern
  (khaled.almahallawy@intel.com)
- ASoC: rt5670: Remove unbalanced pm_runtime_put() (hdegoede@redhat.com)
- ASoC: rockchip: spdif: Add missing clk_disable_unprepare() in
  rk_spdif_runtime_resume() (wangjingjin1@huawei.com)
- ASoC: wm8994: Fix potential deadlock (m.szyprowski@samsung.com)
- ALSA: hda/hdmi: fix stream-id config keep-alive for rt suspend
  (kai.vehmanen@linux.intel.com)
- ALSA: hda/hdmi: set default audio parameters for KAE silent-stream
  (kai.vehmanen@linux.intel.com)
- ALSA: hda/hdmi: fix i915 silent stream programming flow
  (kai.vehmanen@linux.intel.com)
- ASoC: mediatek: mt8183: fix refcount leak in
  mt8183_mt6358_ts3a227_max98357_dev_probe() (wangyufen@huawei.com)
- ASoC: rockchip: pdm: Add missing clk_disable_unprepare() in
  rockchip_pdm_runtime_resume() (wangjingjin1@huawei.com)
- ASoC: audio-graph-card: fix refcount leak of cpu_ep in
  __graph_for_each_link() (wangyufen@huawei.com)
- ASoC: mediatek: mt8173-rt5650-rt5514: fix refcount leak in
  mt8173_rt5650_rt5514_dev_probe() (wangyufen@huawei.com)
- ASoC: Intel: Skylake: Fix driver hang during shutdown
  (cezary.rojewski@intel.com)
- ASoC: sof_es8336: fix possible use-after-free in sof_es8336_remove()
  (yangyingliang@huawei.com)
- hwmon: (jc42) Fix missing unlock on error in jc42_write()
  (yangyingliang@huawei.com)
- orangefs: Fix kmemleak in orangefs_{kernel,client}_debug_init()
  (zhangxiaoxu5@huawei.com)
- orangefs: Fix kmemleak in orangefs_sysfs_init() (zhangxiaoxu5@huawei.com)
- orangefs: Fix kmemleak in orangefs_prepare_debugfs_help_string()
  (zhangxiaoxu5@huawei.com)
- scsi: target: iscsi: Fix a race condition between login_work and the login
  thread (mlombard@redhat.com)
- drm/sti: Fix return type of sti_{dvo,hda,hdmi}_connector_mode_valid()
  (nathan@kernel.org)
- drm/fsl-dcu: Fix return type of fsl_dcu_drm_connector_mode_valid()
  (nathan@kernel.org)
- scsi: smartpqi: Correct device removal for multi-actuator devices
  (Kumar.Meiyappan@microchip.com)
- scsi: smartpqi: Add new controller PCI IDs (mike.mcgowen@microchip.com)
- hugetlbfs: fix null-ptr-deref in hugetlbfs_parse_param() (yin31149@gmail.com)
- scsi: elx: libefc: Fix second parameter type in state callbacks
  (nathan@kernel.org)
- Revert "PCI: Clear PCI_STATUS when setting up device" (bhelgaas@google.com)
- crypto: hisilicon/qm - increase the memory of local variables
  (yekai13@huawei.com)
- scsi: ufs: Reduce the START STOP UNIT timeout (bvanassche@acm.org)
- scsi: lpfc: Fix hard lockup when reading the rx_monitor from debugfs
  (justin.tee@broadcom.com)
- crypto: hisilicon/hpre - fix resource leak in remove process
  (songzhiqi1@huawei.com)
- regulator: core: Fix resolve supply lookup issue (cy_huang@richtek.com)
- Bluetooth: Add quirk to disable MWS Transport Configuration
  (sven@svenpeter.dev)
- Bluetooth: Add quirk to disable extended scanning (sven@svenpeter.dev)
- Bluetooth: hci_bcm: Add CYW4373A0 support (marex@denx.de)
- ice: synchronize the misc IRQ when tearing down Tx tracker
  (jacob.e.keller@intel.com)
- regulator: core: Use different devices for resource allocation and DT lookup
  (cy_huang@richtek.com)
- clk: st: Fix memory leak in st_of_quadfs_setup() (xiujianfeng@huawei.com)
- media: si470x: Fix use-after-free in si470x_int_in_callback()
  (syoshida@redhat.com)
- mmc: sdhci-tegra: Issue CMD and DAT resets together (pshete@nvidia.com)
- mmc: renesas_sdhi: better reset from HS400 mode (wsa+renesas@sang-
  engineering.com)
- mmc: renesas_sdhi: add quirk for broken register layout (wsa+renesas@sang-
  engineering.com)
- mmc: f-sdh30: Add quirks for broken timeout clock capability
  (hayashi.kunihiko@socionext.com)
- nfs: fix possible null-ptr-deref when parsing param (yin31149@gmail.com)
- selftests/bpf: Fix conflicts with built-in functions in bpf_iter_ksym
  (james.hilliard1@gmail.com)
- hwmon: (nct6775) add ASUS CROSSHAIR VIII/TUF/ProArt B550M
  (pauk.denis@gmail.com)
- wifi: mt76: do not run mt76u_status_worker if the device is not running
  (lorenzo@kernel.org)
- regulator: core: fix use_count leakage when handling boot-on
  (zr.zhang@vivo.com)
- libbpf: Avoid enum forward-declarations in public API in C++ mode
  (andrii@kernel.org)
- ASoC: amd: yc: Add Xiaomi Redmi Book Pro 14 2022 into DMI table
  (dukzcry@ya.ru)
- drm/amd/display: Fix DTBCLK disable requests and SRC_SEL programming
  (Alvin.Lee2@amd.com)
- drm/amd/display: Use the largest vready_offset in pipe group
  (Wesley.Chalmers@amd.com)
- drm/amdgpu: Fix potential double free and null pointer dereference
  (windhl@126.com)
- ALSA: usb-audio: Add quirk for Tascam Model 12 (john@metanate.com)
- blk-mq: fix possible memleak when register 'hctx' failed (yebin10@huawei.com)
- media: mediatek: vcodec: Can't set dst buffer to done when lat decode error
  (yunfei.dong@mediatek.com)
- media: dvb-usb: fix memory leak in dvb_usb_adapter_init()
  (mazinalhaddad05@gmail.com)
- media: dvbdev: adopts refcnt to avoid UAF (linma@zju.edu.cn)
- media: dvb-frontends: fix leak of memory fw (yan_lei@dahuatech.com)
- ethtool: avoiding integer overflow in ethtool_phys_id()
  (korotkov.maxim.s@gmail.com)
- bpf: Prevent decl_tag from being referenced in func_proto arg
  (sdf@google.com)
- bpf: Fix a BTF_ID_LIST bug with CONFIG_DEBUG_INFO_BTF not set (yhs@fb.com)
- drm/amd/display: Fix display corruption w/ VSR enable (Ilya.Bakoulin@amd.com)
- ppp: associate skb with a device at tx (sdf@google.com)
- bpf/verifier: Use kmalloc_size_roundup() to match ksize() usage
  (keescook@chromium.org)
- net: ethernet: mtk_eth_soc: drop packets to WDMA if the ring is full
  (nbd@nbd.name)
- mrp: introduce active flags to prevent UAF when applicant uninit
  (schspa@gmail.com)
- ipv6/sit: use DEV_STATS_INC() to avoid data-races (edumazet@google.com)
- net: add atomic_long_t to net_device_stats fields (edumazet@google.com)
- nvme-auth: don't override ctrl keys before validation (sagi@grimberg.me)
- drm/amd/display: fix array index out of bound error in bios parser
  (aurabindo.pillai@amd.com)
- drm/amd/display: Workaround to increase phantom pipe vactive in pipesplit
  (george.shen@amd.com)
- md/raid1: stop mdx_raid1 thread when raid1 array run failed
  (jiang.li@ugreen.com)
- md/raid0, raid10: Don't set discard sectors for request queue
  (xni@redhat.com)
- drivers/md/md-bitmap: check the return value of md_bitmap_get_counter()
  (floridsleeves@gmail.com)
- drm/mediatek: Fix return type of mtk_hdmi_bridge_mode_valid()
  (nathan@kernel.org)
- drm/sti: Use drm_mode_copy() (ville.syrjala@linux.intel.com)
- drm/rockchip: Use drm_mode_copy() (ville.syrjala@linux.intel.com)
- drm/msm: Use drm_mode_copy() (ville.syrjala@linux.intel.com)
- drm/amd/display: Disable DRR actions during state commit
  (Wesley.Chalmers@amd.com)
- drm/amd/display: Use min transition for SubVP into MPO (Alvin.Lee2@amd.com)
- s390/lcs: Fix return type of lcs_start_xmit() (nathan@kernel.org)
- s390/netiucv: Fix return type of netiucv_tx() (nathan@kernel.org)
- s390/ctcm: Fix return type of ctc{mp,}m_tx() (nathan@kernel.org)
- drm/amdgpu: Fix type of second parameter in odn_edit_dpm_table() callback
  (nathan@kernel.org)
- drm/amdgpu: Fix type of second parameter in trans_msg() callback
  (nathan@kernel.org)
- igb: Do not free q_vector unless new one was allocated
  (keescook@chromium.org)
- HID: uclogic: Add support for XP-PEN Deco LW (jose.exposito89@gmail.com)
- HID: input: do not query XP-PEN Deco LW battery (jose.exposito89@gmail.com)
- wifi: brcmfmac: Fix potential NULL pointer dereference in
  'brcmf_c_preinit_dcmds()' (jisoo.jang@yonsei.ac.kr)
- wifi: brcmfmac: Fix potential shift-out-of-bounds in brcmf_fw_alloc_request()
  (linuxlovemin@yonsei.ac.kr)
- hamradio: baycom_epp: Fix return type of baycom_send_packet()
  (nathan@kernel.org)
- net: ethernet: ti: Fix return type of netcp_ndo_start_xmit()
  (nathan@kernel.org)
- bpf: make sure skb->len != 0 when redirecting to a tunneling device
  (sdf@google.com)
- drm/meson: Fix return type of meson_encoder_cvbs_mode_valid()
  (nathan@kernel.org)
- qed (gcc13): use u16 for fid to be big enough (jirislaby@kernel.org)
- wifi: ath11k: Fix qmi_msg_handler data structure initialization
  (quic_rbhattac@quicinc.com)
- HID: apple: enable APPLE_ISO_TILDE_QUIRK for the keyboards of Macs with the
  T2 chip (kekrby@gmail.com)
- HID: apple: fix key translations where multiple quirks attempt to translate
  the same key (kekrby@gmail.com)
- blk-mq: avoid double ->queue_rq() because of early timeout
  (djeffery@redhat.com)
- drm/rockchip: use pm_runtime_resume_and_get() instead of
  pm_runtime_get_sync() (yuancan@huawei.com)
- Revert "drm/amd/display: Limit max DSC target bpp for specific monitors"
  (hamza.mahfooz@amd.com)
- drm/edid: add a quirk for two LG monitors to get them to work on 10bpc
  (hamza.mahfooz@amd.com)
- drm/amd/display: prevent memory leak (gehao@kylinos.cn)
- drm/amd/display: skip commit minimal transition state (zhikai.zhai@amd.com)
- bnx2: Use kmalloc_size_roundup() to match ksize() usage
  (keescook@chromium.org)
- openvswitch: Use kmalloc_size_roundup() to match ksize() usage
  (keescook@chromium.org)
- wifi: ath10k: Delay the unmapping of the buffer (quic_youghand@quicinc.com)
- ipmi: fix memleak when unload ipmi driver (zhangyuchen.lcr@bytedance.com)
- ASoC: Intel: avs: Add quirk for KBL-R RVP platform
  (amadeuszx.slawinski@linux.intel.com)
- ASoC: codecs: rt298: Add quirk for KBL-R RVP platform
  (amadeuszx.slawinski@linux.intel.com)
- wifi: ar5523: Fix use-after-free on ar5523_cmd() timed out
  (syoshida@redhat.com)
- wifi: ath9k: verify the expected usb_endpoints are present
  (pchelkin@ispras.ru)
- brcmfmac: return error when getting invalid max_flowrings from dongle
  (wright.feng@cypress.com)
- media: imx-jpeg: Disable useless interrupt to avoid kernel panic
  (ming.qian@nxp.com)
- drm/etnaviv: add missing quirks for GC300 (doug@schmorgal.com)
- hfs: fix OOB Read in __hfs_brec_find (zhangpeng362@huawei.com)
- ACPI: x86: Add skip i2c clients quirk for Medion Lifetab S10346
  (hdegoede@redhat.com)
- btrfs: do not panic if we can't allocate a prealloc extent state
  (josef@toxicpanda.com)
- ACPI: x86: Add skip i2c clients quirk for Lenovo Yoga Tab 3 Pro (YT3-X90F)
  (hdegoede@redhat.com)
- x86/apic: Handle no CONFIG_X86_X2APIC on systems with x2APIC enabled by BIOS
  (mat.jonczyk@o2.pl)
- acct: fix potential integer overflow in encode_comp_t()
  (zhengyejian1@huawei.com)
- nilfs2: fix shift-out-of-bounds due to too large exponent of block size
  (konishi.ryusuke@gmail.com)
- nilfs2: fix shift-out-of-bounds/overflow in nilfs_sb2_bad_offset()
  (konishi.ryusuke@gmail.com)
- ACPI: video: Add force_native quirk for Sony Vaio VPCY11S1E
  (hdegoede@redhat.com)
- ACPI: video: Add force_vendor quirk for Sony Vaio PCG-FRV35
  (hdegoede@redhat.com)
- ACPI: video: Change Sony Vaio VPCEH3U1E quirk to force_native
  (hdegoede@redhat.com)
- ACPI: video: Change GIGABYTE GB-BXBT-2807 quirk to force_none
  (hdegoede@redhat.com)
- thermal/core: Ensure that thermal device is registered in
  thermal_zone_get_temp (linux@roeck-us.net)
- ACPICA: Fix error code path in acpi_ds_call_control_method()
  (rafael.j.wysocki@intel.com)
- ACPI: EC: Add quirk for the HP Pavilion Gaming 15-cx0041ur
  (chad@redpilled.dev)
- ACPI: processor: idle: Check acpi_fetch_acpi_dev() return value
  (floridsleeves@gmail.com)
- fs: jfs: fix shift-out-of-bounds in dbDiscardAG (wuhoipok@gmail.com)
- jfs: Fix fortify moan in symlink (linux@treblig.org)
- udf: Avoid double brelse() in udf_rename() (syoshida@redhat.com)
- fs: jfs: fix shift-out-of-bounds in dbAllocAG (mudongliangabcd@gmail.com)
- arm64: dts: qcom: sm6350: Add apps_smmu with streamID to SDHCI 1/2 nodes
  (marijn.suijten@somainline.org)
- arm64: dts: qcom: sm8450: disable SDHCI SDR104/SDR50 on all boards
  (krzysztof.kozlowski@linaro.org)
- binfmt_misc: fix shift-out-of-bounds in check_special_flags
  (liushixin2@huawei.com)
- x86/hyperv: Remove unregister syscore call from Hyper-V cleanup
  (gauravkohli@linux.microsoft.com)
- video: hyperv_fb: Avoid taking busy spinlock on panic path
  (gpiccoli@igalia.com)
- ARM: dts: aspeed: rainier,everest: Move reserved memory regions
  (anoo@us.ibm.com)
- arm64: make is_ttbrX_addr() noinstr-safe (mark.rutland@arm.com)
- rcu: Fix __this_cpu_read() lockdep warning in rcu_force_quiescent_state()
  (qiang1.zhang@intel.com)
- net: fec: check the return value of build_skb() (wei.fang@nxp.com)
- HID: amd_sfh: Add missing check for dma_alloc_coherent (jiasheng@iscas.ac.cn)
- mctp: Remove device type check at unregister (matt@codeconstruct.com.au)
- net: dsa: microchip: remove IRQF_TRIGGER_FALLING in request_threaded_irq
  (arun.ramadoss@microchip.com)
- cifs: don't leak -ENOMEM in smb2_open_file() (pc@cjr.nz)
- mctp: serial: Fix starting value for frame check sequence
  (jk@codeconstruct.com.au)
- net: stream: purge sk_error_queue in sk_stream_kill_queues()
  (edumazet@google.com)
- myri10ge: Fix an error handling path in myri10ge_probe()
  (christophe.jaillet@wanadoo.fr)
- rxrpc: Fix missing unlock in rxrpc_do_sendmsg() (dhowells@redhat.com)
- net_sched: reject TCF_EM_SIMPLE case for complex ematch module
  (cong.wang@bytedance.com)
- mailbox: zynq-ipi: fix error handling while device_register() fails
  (yangyingliang@huawei.com)
- mailbox: arm_mhuv2: Fix return value check in mhuv2_probe()
  (yangyingliang@huawei.com)
- mailbox: mpfs: read the system controller's status
  (conor.dooley@microchip.com)
- skbuff: Account for tail adjustment during pull operations
  (quic_subashab@quicinc.com)
- devlink: protect devlink dump by the instance lock (kuba@kernel.org)
- arm64: dts: mt8183: Fix Mali GPU clock (wenst@chromium.org)
- soc: mediatek: pm-domains: Fix the power glitch issue (chun-
  jie.chen@mediatek.com)
- openvswitch: Fix flow lookup to use unmasked key (echaudro@redhat.com)
- selftests: devlink: fix the fd redirect in dummy_reporter_test
  (kuba@kernel.org)
- devlink: hold region lock when flushing snapshots (kuba@kernel.org)
- rtc: mxc_v2: Add missing clk_disable_unprepare() (guozihua@huawei.com)
- igc: Set Qbv start_time and end_time to end_time if not being configured in
  GCL (tee.min.tan@linux.intel.com)
- igc: recalculate Qbv end_time by considering cycle time
  (tee.min.tan@linux.intel.com)
- igc: allow BaseTime 0 enrollment for Qbv (tee.min.tan@linux.intel.com)
- igc: Add checking for basetime less than zero
  (muhammad.husaini.zulkifli@intel.com)
- igc: Use strict cycles for Qbv scheduling (vinicius.gomes@intel.com)
- igc: Enhance Qbv scheduling by using first flag bit
  (vinicius.gomes@intel.com)
- net: dsa: mv88e6xxx: avoid reg_lock deadlock in mv88e6xxx_setup_port()
  (vladimir.oltean@nxp.com)
- r6040: Fix kmemleak in probe and remove (lizetao1@huawei.com)
- unix: Fix race in SOCK_SEQPACKET's unix_dgram_sendmsg() (tkhai@ya.ru)
- nfc: pn533: Clear nfc_target before being used (linuxlovemin@yonsei.ac.kr)
- net: enetc: avoid buffer leaks on xdp_do_redirect() failure
  (vladimir.oltean@nxp.com)
- media: v4l2-ctrls-api.c: add back dropped ctrl->is_new = 1 (hverkuil-
  cisco@xs4all.nl)
- bpf: prevent leak of lsm program after failed attach (milan@mdaverde.com)
- selftests/bpf: Select CONFIG_FUNCTION_ERROR_INJECTION (song@kernel.org)
- block, bfq: fix possible uaf for 'bfqq->bic' (yukuai3@huawei.com)
- mISDN: hfcmulti: don't call dev_kfree_skb/kfree_skb() under
  spin_lock_irqsave() (yangyingliang@huawei.com)
- mISDN: hfcpci: don't call dev_kfree_skb/kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- mISDN: hfcsusb: don't call dev_kfree_skb/kfree_skb() under
  spin_lock_irqsave() (yangyingliang@huawei.com)
- bonding: do failover when high prio link up (liuhangbin@gmail.com)
- bonding: add missed __rcu annotation for curr_active_slave
  (liuhangbin@gmail.com)
- net: macsec: fix net device access prior to holding a lock
  (ehakim@nvidia.com)
- nfsd: under NFSv4.1, fix double svc_xprt_put on rpc_create failure
  (dan.aloni@vastdata.com)
- iommu/mediatek: Fix forever loop in error handling (error27@gmail.com)
- rtc: pcf85063: fix pcf85063_clkout_control (alexandre.belloni@bootlin.com)
- rtc: pic32: Move devm_rtc_allocate_device earlier in pic32_rtc_probe()
  (cuigaosheng1@huawei.com)
- rtc: st-lpc: Add missing clk_disable_unprepare in st_rtc_probe()
  (cuigaosheng1@huawei.com)
- netfilter: flowtable: really fix NAT IPv6 offload (dqfext@gmail.com)
- mfd: pm8008: Fix return value check in pm8008_probe()
  (yangyingliang@huawei.com)
- mfd: qcom_rpm: Fix an error handling path in qcom_rpm_probe()
  (christophe.jaillet@wanadoo.fr)
- mfd: bd957x: Fix Kconfig dependency on REGMAP_IRQ
  (matti.vaittinen@fi.rohmeurope.com)
- mfd: axp20x: Do not sleep in the power off handler (samuel@sholland.org)
- dt-bindings: mfd: qcom,spmi-pmic: Drop PWM reg dependency
  (bryan.odonoghue@linaro.org)
- powerpc/pseries/eeh: use correct API for error log size
  (nathanl@linux.ibm.com)
- remoteproc: qcom: q6v5: Fix missing clk_disable_unprepare() in
  q6v5_wcss_qcs404_power_on() (shangxiaojing@huawei.com)
- remoteproc: qcom_q6v5_pas: Fix missing of_node_put() in
  adsp_alloc_memory_region() (yuancan@huawei.com)
- remoteproc: qcom_q6v5_pas: detach power domains on remove
  (luca.weiss@fairphone.com)
- remoteproc: qcom_q6v5_pas: disable wakeup on probe fail or remove
  (luca.weiss@fairphone.com)
- remoteproc: qcom: q6v5: Fix potential null-ptr-deref in q6v5_wcss_init_mmio()
  (shangxiaojing@huawei.com)
- remoteproc: sysmon: fix memory leak in qcom_add_sysmon_subdev()
  (cuigaosheng1@huawei.com)
- RISC-V: KVM: Fix reg_val check in kvm_riscv_vcpu_set_reg_config()
  (apatel@ventanamicro.com)
- pwm: mediatek: always use bus clock for PWM on MT7622 (daniel@makrotopia.org)
- pwm: mtk-disp: Fix the parameters calculated by the enabled flag of disp_pwm
  (xinlei.lee@mediatek.com)
- pwm: sifive: Call pwm_sifive_update_clock() while mutex is held (u.kleine-
  koenig@pengutronix.de)
- iommu/sun50i: Remove IOMMU_DOMAIN_IDENTITY (jgg@nvidia.com)
- iommu/mediatek: Validate number of phandles associated with "mediatek,larbs"
  (groeck@chromium.org)
- iommu/mediatek: Add error path for loop of mm_dts_parse
  (yong.wu@mediatek.com)
- iommu/mediatek: Use component_match_add (yong.wu@mediatek.com)
- iommu/mediatek: Add platform_device_put for recovering the device refcnt
  (yong.wu@mediatek.com)
- selftests/powerpc: Fix resource leaks (linmq006@gmail.com)
- powerpc/hv-gpci: Fix hv_gpci event list (kjain@linux.ibm.com)
- powerpc/83xx/mpc832x_rdb: call platform_device_put() in error case in
  of_fsl_spi_probe() (yangyingliang@huawei.com)
- powerpc/perf: callchain validate kernel stack pointer bounds
  (npiggin@gmail.com)
- powerpc: dts: turris1x.dts: Add channel labels for temperature sensor
  (pali@kernel.org)
- kprobes: Fix check for probe enabled in kill_kprobe() (lihuafei1@huawei.com)
- powerpc/pseries: fix plpks_read_var() code for different consumers
  (nayna@linux.ibm.com)
- powerpc/pseries: Return -EIO instead of -EINTR for H_ABORTED error
  (nayna@linux.ibm.com)
- powerpc/pseries: Fix the H_CALL error code in PLPKS driver
  (nayna@linux.ibm.com)
- powerpc/pseries: fix the object owners enum value in plpks driver
  (nayna@linux.ibm.com)
- powerpc/xive: add missing iounmap() in error path in
  xive_spapr_populate_irq_data() (yangyingliang@huawei.com)
- powerpc/xmon: Fix -Wswitch-unreachable warning in bpt_cmds
  (gustavoars@kernel.org)
- cxl: Fix refcount leak in cxl_calc_capp_routing (linmq006@gmail.com)
- powerpc/52xx: Fix a resource leak in an error handling path
  (christophe.jaillet@wanadoo.fr)
- macintosh/macio-adb: check the return value of ioremap()
  (studentxswpy@163.com)
- macintosh: fix possible memory leak in macio_add_one_device()
  (yangyingliang@huawei.com)
- iommu/fsl_pamu: Fix resource leak in fsl_pamu_probe() (yuancan@huawei.com)
- iommu/amd: Fix pci device refcount leak in ppr_notifier()
  (yangyingliang@huawei.com)
- iommu: Avoid races around device probe (robin.murphy@arm.com)
- iommu/mediatek: Check return value after calling platform_get_resource()
  (yangyingliang@huawei.com)
- rtc: pcf85063: Fix reading alarm (alexander.stein@ew.tq-group.com)
- rtc: snvs: Allow a time difference on clock register read
  (stefan.eichenberger@toradex.com)
- rtc: cmos: Disable ACPI RTC event on removal (rafael.j.wysocki@intel.com)
- rtc: cmos: Rename ACPI-related functions (rafael.j.wysocki@intel.com)
- rtc: cmos: Eliminate forward declarations of some functions
  (rafael.j.wysocki@intel.com)
- rtc: cmos: Call rtc_wake_setup() from cmos_do_probe()
  (rafael.j.wysocki@intel.com)
- rtc: cmos: Call cmos_wake_setup() from cmos_do_probe()
  (rafael.j.wysocki@intel.com)
- rtc: pcf2127: Convert to .probe_new() (u.kleine-koenig@pengutronix.de)
- rtc: class: Fix potential memleak in devm_rtc_allocate_device()
  (shangxiaojing@huawei.com)
- rtc: rzn1: Check return value in rzn1_rtc_probe (katrinzhou@tencent.com)
- dmaengine: idxd: Fix crc_val field for completion record
  (fenghua.yu@intel.com)
- fs/ntfs3: Fix slab-out-of-bounds read in ntfs_trim_fs
  (abdun.nihaal@gmail.com)
- phy: qcom-qmp-pcie: Fix sm8450_qmp_gen4x2_pcie_pcs_tbl[] register names
  (manivannan.sadhasivam@linaro.org)
- phy: qcom-qmp-pcie: Fix high latency with 4x2 PHY when ASPM is enabled
  (manivannan.sadhasivam@linaro.org)
- phy: qcom-qmp-pcie: Support SM8450 PCIe1 PHY in EP mode
  (dmitry.baryshkov@linaro.org)
- phy: qcom-qmp-pcie: support separate tables for EP mode
  (dmitry.baryshkov@linaro.org)
- phy: qcom-qmp-pcie: split pcs_misc init cfg for ipq8074 pcs table
  (ansuelsmth@gmail.com)
- phy: qcom-qmp-pcie: split register tables into common and extra parts
  (dmitry.baryshkov@linaro.org)
- pwm: tegra: Ensure the clock rate is not less than needed
  (jonathanh@nvidia.com)
- pwm: tegra: Improve required rate calculation (jonathanh@nvidia.com)
- include/uapi/linux/swab: Fix potentially missing __always_inline
  (matt.redfearn@mips.com)
- phy: usb: Fix clock imbalance for suspend/resume (justinpopo6@gmail.com)
- phy: usb: Use slow clock for wake enabled suspend (justinpopo6@gmail.com)
- phy: usb: s2 WoL wakeup_count not incremented for USB->Eth devices
  (alcooperx@gmail.com)
- phy: qcom-qmp-usb: fix sc8280xp PCS_USB offset (johan+linaro@kernel.org)
- dmaengine: idxd: Make read buffer sysfs attributes invisible for Intel IAA
  (xiaochen.shen@intel.com)
- iommu/rockchip: fix permission bits in page table entries v2
  (michael.riesch@wolfvision.net)
- iommu/sun50i: Implement .iotlb_sync_map (jernej.skrabec@gmail.com)
- iommu/sun50i: Fix flush size (jernej.skrabec@gmail.com)
- iommu/sun50i: Fix R/W permission check (jernej.skrabec@gmail.com)
- iommu/sun50i: Consider all fault sources for reset (jernej.skrabec@gmail.com)
- iommu/sun50i: Fix reset release (jernej.skrabec@gmail.com)
- iommu/s390: Fix duplicate domain attachments (schnelle@linux.ibm.com)
- phy: qcom-qmp-usb: correct registers layout for IPQ8074 USB3 PHY
  (dmitry.baryshkov@linaro.org)
- phy: qcom-qmp-usb: drop start and pwrdn-ctrl abstraction
  (johan+linaro@kernel.org)
- phy: qcom-qmp-usb: clean up status polling (johan+linaro@kernel.org)
- phy: qcom-qmp-usb: drop power-down delay config (johan+linaro@kernel.org)
- phy: qcom-qmp-usb: drop sc8280xp power-down delay (johan+linaro@kernel.org)
- phy: qcom-qmp-usb: clean up power-down handling (johan+linaro@kernel.org)
- phy: qcom-qmp-pcie: fix ipq6018 initialisation (johan+linaro@kernel.org)
- phy: qcom-qmp-pcie: fix ipq8074-gen3 initialisation (johan+linaro@kernel.org)
- phy: qcom-qmp-pcie: fix sc8180x initialisation (johan+linaro@kernel.org)
- phy: qcom-qmp-pcie: replace power-down delay (johan+linaro@kernel.org)
- phy: qcom-qmp-pcie: drop power-down delay config (johan+linaro@kernel.org)
- remoteproc: core: Auto select rproc-virtio device id (shengjiu.wang@nxp.com)
- dmaengine: apple-admac: Allocate cache SRAM to channels
  (povik+lin@cutebit.org)
- dmaengine: idxd: Make max batch size attributes in sysfs invisible for Intel
  IAA (xiaochen.shen@intel.com)
- phy: qcom-qmp-pcie: drop bogus register update (johan+linaro@kernel.org)
- phy: marvell: phy-mvebu-a3700-comphy: Reset COMPHY registers before USB 3.0
  power on (pali@kernel.org)
- fs/ntfs3: Harden against integer overflows (dan.carpenter@oracle.com)
- fs/ntfs3: Avoid UBSAN error on true_sectors_per_clst() (syoshida@redhat.com)
- RDMA/siw: Fix pointer cast warning (arnd@arndb.de)
- perf stat: Do not delay the workload with --delay (namhyung@kernel.org)
- ftrace: Allow WITH_ARGS flavour of graph tracer with shadow call stack
  (ardb@kernel.org)
- perf off_cpu: Fix a typo in BTF tracepoint name, it should be
  'btf_trace_sched_switch' (namhyung@kernel.org)
- leds: is31fl319x: Fix setting current limit for is31fl319{0,1,3}
  (luca@z3ntu.xyz)
- gfs2: Partially revert gfs2_inode_lookup change (agruenba@redhat.com)
- power: supply: fix null pointer dereferencing in
  power_supply_get_battery_info (ruanjinjie@huawei.com)
- perf branch: Fix interpretation of branch records (james.clark@arm.com)
- power: supply: bq25890: Ensure pump_express_work is cancelled on remove
  (hdegoede@redhat.com)
- power: supply: bq25890: Convert to i2c's .probe_new() (u.kleine-
  koenig@pengutronix.de)
- power: supply: bq25890: Factor out regulator registration code
  (marex@denx.de)
- power: supply: Fix refcount leak in rk817_charger_probe
  (linqiheng@huawei.com)
- power: supply: ab8500: Fix error handling in ab8500_charger_init()
  (yuancan@huawei.com)
- HSI: omap_ssi_core: Fix error handling in ssi_init() (yuancan@huawei.com)
- power: supply: cw2015: Fix potential null-ptr-deref in cw_bat_probe()
  (shangxiaojing@huawei.com)
- power: supply: z2_battery: Fix possible memleak in z2_batt_probe()
  (zhangqilong3@huawei.com)
- perf symbol: correction while adjusting symbol (akaher@vmware.com)
- perf trace: Handle failure when trace point folder is missed
  (leo.yan@linaro.org)
- perf trace: Use macro RAW_SYSCALL_ARGS_NUM to replace number
  (leo.yan@linaro.org)
- perf trace: Return error if a system call doesn't exist (leo.yan@linaro.org)
- watchdog: iTCO_wdt: Set NO_REBOOT if the watchdog is not already running
  (mika.westerberg@linux.intel.com)
- power: supply: fix residue sysfs file in error handle route of
  __power_supply_register() (zengheng4@huawei.com)
- HSI: omap_ssi_core: fix possible memory leak in ssi_probe()
  (yangyingliang@huawei.com)
- HSI: omap_ssi_core: fix unbalanced pm_runtime_disable()
  (yangyingliang@huawei.com)
- perf stat: Move common code in print_metric_headers() (namhyung@kernel.org)
- perf stat: Use evsel__is_hybrid() more (namhyung@kernel.org)
- perf tools: Fix "kernel lock contention analysis" test by not printing
  warnings in quiet mode (james.clark@arm.com)
- led: qcom-lpg: Fix sleeping in atomic (dmitry.baryshkov@linaro.org)
- fbdev: uvesafb: Fixes an error handling path in uvesafb_probe()
  (christophe.jaillet@wanadoo.fr)
- fbdev: uvesafb: don't build on UML (rdunlap@infradead.org)
- fbdev: geode: don't build on UML (rdunlap@infradead.org)
- fbdev: ep93xx-fb: Add missing clk_disable_unprepare in ep93xxfb_probe()
  (cuigaosheng1@huawei.com)
- fbdev: vermilion: decrease reference count in error path
  (wangxiongfeng2@huawei.com)
- fbdev: via: Fix error in via_core_init() (shangxiaojing@huawei.com)
- fbdev: pm2fb: fix missing pci_disable_device() (yangyingliang@huawei.com)
- fbdev: ssd1307fb: Drop optional dependency
  (andriy.shevchenko@linux.intel.com)
- thermal/drivers/qcom/lmh: Fix irq handler return value
  (bjorn.andersson@linaro.org)
- thermal/drivers/qcom/temp-alarm: Fix inaccurate warning for gen2
  (luca.weiss@fairphone.com)
- thermal/of: Fix memory leak on thermal_of_zone_register() failure
  (idosch@nvidia.com)
- thermal/drivers/k3_j72xx_bandgap: Fix the debug print message
  (j-keerthy@ti.com)
- thermal/drivers/imx8mm_thermal: Validate temperature range
  (marcus.folkesson@gmail.com)
- samples: vfio-mdev: Fix missing pci_disable_device() in mdpy_fb_probe()
  (shangxiaojing@huawei.com)
- ksmbd: Fix resource leak in ksmbd_session_rpc_open() (xiujianfeng@huawei.com)
- tracing/hist: Fix issue of losting command info in error_log
  (zhengyejian1@huawei.com)
- usb: typec: wusb3801: fix fwnode refcount leak in wusb3801_probe()
  (yangyingliang@huawei.com)
- usb: storage: Add check for kcalloc (jiasheng@iscas.ac.cn)
- i2c: ismt: Fix an out-of-bounds bug in ismt_access() (zheyuma97@gmail.com)
- i2c: mux: reg: check return value after calling platform_get_resource()
  (yangyingliang@huawei.com)
- gpiolib: protect the GPIO device against being dropped while in use by user-
  space (bartosz.golaszewski@linaro.org)
- gpiolib: cdev: fix NULL-pointer dereferences (bartosz.golaszewski@linaro.org)
- vme: Fix error not catched in fake_init() (chenzhongjin@huawei.com)
- staging: rtl8192e: Fix potential use-after-free in rtllib_rx_Monitor()
  (yuehaibing@huawei.com)
- staging: rtl8192u: Fix use after free in ieee80211_rx() (error27@gmail.com)
- i2c: pxa-pci: fix missing pci_disable_device() on error in ce4100_i2c_probe
  (tanghui20@huawei.com)
- vfio/iova_bitmap: refactor iova_bitmap_set() to better handle page boundaries
  (joao.m.martins@oracle.com)
- chardev: fix error handling in cdev_device_add() (yangyingliang@huawei.com)
- mcb: mcb-parse: fix error handing in chameleon_parse_gdd()
  (yangyingliang@huawei.com)
- drivers: mcb: fix resource leak in mcb_probe() (shaozhengchao@huawei.com)
- usb: gadget: f_hid: fix refcount leak on error path (john@metanate.com)
- usb: gadget: f_hid: fix f_hidg lifetime vs cdev (john@metanate.com)
- usb: core: hcd: Fix return value check in usb_hcd_setup_local_mem()
  (yangyingliang@huawei.com)
- usb: roles: fix of node refcount leak in usb_role_switch_is_parent()
  (yangyingliang@huawei.com)
- tracing/user_events: Fix call print_fmt leak (beaub@linux.microsoft.com)
- coresight: cti: Fix null pointer error on CTI init before ETM
  (mike.leach@linaro.org)
- coresight: trbe: remove cpuhp instance node before remove cpuhp state
  (shenyang39@huawei.com)
- counter: stm32-lptimer-cnt: fix the check on arr and cmp registers update
  (fabrice.gasnier@foss.st.com)
- iio: adis: add '__adis_enable_irq()' implementation
  (ramona.bolboaca@analog.com)
- iio: temperature: ltc2983: make bulk write buffer DMA-safe
  (cosmin.tanislav@analog.com)
- cxl: fix possible null-ptr-deref in cxl_pci_init_afu|adapter()
  (yangyingliang@huawei.com)
- cxl: fix possible null-ptr-deref in cxl_guest_init_afu|adapter()
  (yangyingliang@huawei.com)
- firmware: raspberrypi: fix possible memory leak in rpi_firmware_probe()
  (yangyingliang@huawei.com)
- misc: sgi-gru: fix use-after-free error in gru_set_context_option, gru_fault
  and gru_handle_user_call_os (zyytlz.wz@163.com)
- misc: tifm: fix possible memory leak in tifm_7xx1_switch_media()
  (ruanjinjie@huawei.com)
- ocxl: fix pci device refcount leak when calling get_function_0()
  (yangyingliang@huawei.com)
- misc: ocxl: fix possible name leak in ocxl_file_register_afu()
  (yangyingliang@huawei.com)
- test_firmware: fix memory leak in test_firmware_init()
  (shaozhengchao@huawei.com)
- habanalabs: fix return value check in hl_fw_get_sec_attest_data()
  (yangyingliang@huawei.com)
- serial: sunsab: Fix error handling in sunsab_init() (yuancan@huawei.com)
- serial: altera_uart: fix locking in polling mode (gsomlo@gmail.com)
- serial: pch: Fix PCI device refcount leak in pch_request_dma()
  (wangxiongfeng2@huawei.com)
- serial: stm32: move dma_request_chan() before clk_prepare_enable()
  (valentin.caron@foss.st.com)
- serial: pl011: Do not clear RX FIFO & RX interrupt in unthrottle.
  (delisun@pateo.com.cn)
- serial: amba-pl011: avoid SBSA UART accessing DMACR register
  (jiamei.xie@arm.com)
- USB: gadget: Fix use-after-free during usb config switch
  (water.zhangjiantao@huawei.com)
- extcon: usbc-tusb320: Update state on probe even if no IRQ pending
  (marex@denx.de)
- usb: musb: omap2430: Fix probe regression for missing resources
  (tony@atomide.com)
- usb: typec: tipd: Fix typec_unregister_port error paths (sven@svenpeter.dev)
- usb: typec: tipd: Fix spurious fwnode_handle_put in error path
  (sven@svenpeter.dev)
- usb: typec: tipd: Cleanup resources if devm_tps6598_psy_register fails
  (sven@svenpeter.dev)
- usb: typec: tcpci: fix of node refcount leak in tcpci_register_port()
  (yangyingliang@huawei.com)
- usb: typec: Check for ops->exit instead of ops->enter in altmode_exit
  (sven@svenpeter.dev)
- staging: vme_user: Fix possible UAF in tsi148_dma_list_add
  (cuigaosheng1@huawei.com)
- interconnect: qcom: sc7180: fix dropped const of qcom_icc_bcm
  (krzysztof.kozlowski@linaro.org)
- usb: fotg210-udc: Fix ages old endianness issues (linus.walleij@linaro.org)
- uio: uio_dmem_genirq: Fix deadlock between irq config and handling
  (rafaelmendsr@gmail.com)
- uio: uio_dmem_genirq: Fix missing unlock in irq configuration
  (rafaelmendsr@gmail.com)
- vfio/iova_bitmap: Fix PAGE_SIZE unaligned bitmaps (joao.m.martins@oracle.com)
- vfio: platform: Do not pass return buffer to ACPI _RST method
  (rafaelmendsr@gmail.com)
- class: fix possible memory leak in __class_register()
  (yangyingliang@huawei.com)
- drivers: staging: r8188eu: Fix sleep-in-atomic-context bug in
  rtw_join_timeout_handler (duoming@zju.edu.cn)
- serial: 8250_bcm7271: Fix error handling in brcmuart_init()
  (yuancan@huawei.com)
- serial: tegra: Read DMA status before terminating (kkartik@nvidia.com)
- drivers: dio: fix possible memory leak in dio_init()
  (yangyingliang@huawei.com)
- riscv: Fix P4D_SHIFT definition for 3-level page table mode
  (alexghiti@rivosinc.com)
- f2fs: fix iostat parameter for discard (frank.li@vivo.com)
- RISC-V: Align the shadow stack (palmer@rivosinc.com)
- IB/IPoIB: Fix queue count inconsistency for PKEY child interfaces
  (dtatulea@nvidia.com)
- hwrng: geode - Fix PCI device refcount leak (wangxiongfeng2@huawei.com)
- hwrng: amd - Fix PCI device refcount leak (wangxiongfeng2@huawei.com)
- crypto: img-hash - Fix variable dereferenced before check 'hdev->req'
  (cuigaosheng1@huawei.com)
- riscv: Fix crash during early errata patching (samuel@sholland.org)
- RISC-V: Fix MEMREMAP_WB for systems with Svpbmt (apatel@ventanamicro.com)
- RISC-V: Fix unannoted hardirqs-on in return to userspace slow-path
  (abrestic@rivosinc.com)
- RDMA/hns: Fix XRC caps on HIP08 (tangchengchang@huawei.com)
- RDMA/hns: Fix error code of CMD (tangchengchang@huawei.com)
- RDMA/hns: Fix page size cap from firmware (tangchengchang@huawei.com)
- RDMA/hns: Fix PBL page MTR find (tangchengchang@huawei.com)
- RDMA/hns: Fix AH attr queried by query_qp (tangchengchang@huawei.com)
- RDMA/hns: Fix the gid problem caused by free mr (liuyixing1@huawei.com)
- orangefs: Fix sysfs not cleanup when dev init failed
  (zhangxiaoxu5@huawei.com)
- PCI: vmd: Fix secondary bus reset for Intel bridges
  (francisco.munoz.ruiz@linux.intel.com)
- RDMA/srp: Fix error return code in srp_parse_options() (wangyufen@huawei.com)
- RDMA/hfi1: Fix error return code in parse_platform_config()
  (wangyufen@huawei.com)
- RDMA: Disable IB HW for UML (rdunlap@infradead.org)
- riscv/mm: add arch hook arch_clear_hugepage_flags (tongtiangen@huawei.com)
- crypto: omap-sham - Use pm_runtime_resume_and_get() in omap_sham_probe()
  (shangxiaojing@huawei.com)
- crypto: amlogic - Remove kcalloc without check
  (christophe.jaillet@wanadoo.fr)
- crypto: qat - fix error return code in adf_probe (wangyufen@huawei.com)
- RDMA/nldev: Fix failure to send large messages (markzhang@nvidia.com)
- f2fs: avoid victim selection from previous victim section
  (yonggil.song@samsung.com)
- f2fs: fix to enable compress for newly created file if extension matches
  (shengyong@oppo.com)
- f2fs: set zstd compress level correctly (shengyong@oppo.com)
- RDMA/nldev: Add checks for nla_nest_start() in fill_stat_counter_qps()
  (yuancan@huawei.com)
- scsi: ufs: core: Fix the polling implementation (bvanassche@acm.org)
- scsi: snic: Fix possible UAF in snic_tgt_create() (cuigaosheng1@huawei.com)
- scsi: fcoe: Fix transport not deattached when fcoe_if_init() fails
  (chenzhongjin@huawei.com)
- scsi: ipr: Fix WARNING in ipr_init() (shangxiaojing@huawei.com)
- scsi: scsi_debug: Fix possible name leak in sdebug_add_host_helper()
  (yangyingliang@huawei.com)
- scsi: fcoe: Fix possible name leak when device_register() fails
  (yangyingliang@huawei.com)
- scsi: scsi_debug: Fix a warning in resp_report_zones()
  (harshit.m.mogalapalli@oracle.com)
- scsi: scsi_debug: Fix a warning in resp_verify()
  (harshit.m.mogalapalli@oracle.com)
- scsi: efct: Fix possible memleak in efct_device_init()
  (chenzhongjin@huawei.com)
- scsi: hpsa: Fix possible memory leak in hpsa_add_sas_device()
  (yangyingliang@huawei.com)
- scsi: hpsa: Fix error handling in hpsa_add_sas_host()
  (yangyingliang@huawei.com)
- scsi: mpt3sas: Fix possible resource leaks in mpt3sas_transport_port_add()
  (yangyingliang@huawei.com)
- crypto: hisilicon/qm - fix 'QM_XEQ_DEPTH_CAP' mask value
  (qianweili@huawei.com)
- crypto: arm64/sm3 - fix possible crash with CFI enabled (ebiggers@google.com)
- crypto: arm64/sm3 - add NEON assembly implementation
  (tianjia.zhang@linux.alibaba.com)
- crypto: x86/sm4 - fix crash with CFI enabled (ebiggers@google.com)
- crypto: x86/sm3 - fix possible crash with CFI enabled (ebiggers@google.com)
- crypto: x86/sha512 - fix possible crash with CFI enabled
  (ebiggers@google.com)
- crypto: x86/sha256 - fix possible crash with CFI enabled
  (ebiggers@google.com)
- crypto: x86/sha1 - fix possible crash with CFI enabled (ebiggers@google.com)
- crypto: x86/aria - fix crash with CFI enabled (ebiggers@google.com)
- crypto: x86/aegis128 - fix possible crash with CFI enabled
  (ebiggers@google.com)
- padata: Fix list iterator in padata_do_serial() (daniel.m.jordan@oracle.com)
- padata: Always leave BHs disabled when running ->parallel()
  (daniel.m.jordan@oracle.com)
- crypto: tcrypt - Fix multibuffer skcipher speed test mem leak
  (zhangyiqun@phytium.com.cn)
- scsi: hpsa: Fix possible memory leak in hpsa_init_one() (yuancan@huawei.com)
- PCI: endpoint: pci-epf-vntb: Fix call pci_epc_mem_free_addr() in error path
  (frank.li@nxp.com)
- dt-bindings: visconti-pcie: Fix interrupts array max constraints
  (Sergey.Semin@baikalelectronics.ru)
- dt-bindings: imx6q-pcie: Fix clock names for imx6sx and imx8mq
  (Sergey.Semin@baikalelectronics.ru)
- RDMA/rxe: Fix NULL-ptr-deref in rxe_qp_do_cleanup() when socket create failed
  (zhangxiaoxu5@huawei.com)
- RDMA/hns: fix memory leak in hns_roce_alloc_mr() (shaozhengchao@huawei.com)
- RDMA/irdma: Initialize net_type before checking it (mustafa.ismail@intel.com)
- crypto: ccree - Make cc_debugfs_global_fini() available for module init
  function (u.kleine-koenig@pengutronix.de)
- RDMA/hfi: Decrease PCI device reference count in error path
  (wangxiongfeng2@huawei.com)
- PCI: Check for alloc failure in pci_request_irq() (zengheng4@huawei.com)
- RDMA/hns: Fix incorrect sge nums calculation (luoyouming@huawei.com)
- RDMA/hns: Fix ext_sge num error when post send (luoyouming@huawei.com)
- RDMA/rxe: Fix mr->map double free (lizhijian@fujitsu.com)
- crypto: hisilicon/qm - add missing pci_dev_put() in q_num_set()
  (wangxiongfeng2@huawei.com)
- crypto: cryptd - Use request context instead of stack for sub-request
  (herbert@gondor.apana.org.au)
- crypto: ccree - Remove debugfs when platform_driver_register failed
  (cuigaosheng1@huawei.com)
- scsi: scsi_debug: Fix a warning in resp_write_scat()
  (harshit.m.mogalapalli@oracle.com)
- RDMA/irdma: Do not request 2-level PBLEs for CQ alloc
  (mustafa.ismail@intel.com)
- RDMA/irdma: Fix RQ completion opcode (mustafa.ismail@intel.com)
- RDMA/irdma: Fix inline for multiple SGE's (mustafa.ismail@intel.com)
- RDMA/siw: Set defined status for work completion with undefined status
  (bmt@zurich.ibm.com)
- RDMA/nldev: Return "-EAGAIN" if the cm_id isn't from expected port
  (markzhang@nvidia.com)
- RDMA/core: Make sure "ib_port" is valid when access sysfs node
  (markzhang@nvidia.com)
- RDMA/restrack: Release MR restrack when delete (markzhang@nvidia.com)
- f2fs: fix to avoid accessing uninitialized spinlock (chao@kernel.org)
- PCI: imx6: Initialize PHY before deasserting core reset
  (s.hauer@pengutronix.de)
- PCI: vmd: Disable MSI remapping after suspend (nirmal.patel@linux.intel.com)
- IB/mad: Don't call to function that might sleep while in atomic context
  (lravich@gmail.com)
- RDMA/siw: Fix immediate work request flush to completion queue
  (bmt@zurich.ibm.com)
- scsi: qla2xxx: Fix set-but-not-used variable warnings (bvanassche@acm.org)
- RDMA/irdma: Report the correct link speed (shiraz.saleem@intel.com)
- f2fs: fix to destroy sbi->post_read_wq in error path of f2fs_fill_super()
  (chao@kernel.org)
- f2fs: fix the assign logic of iocb (quic_mojha@quicinc.com)
- f2fs: allow to set compression for inlined file (jaegeuk@kernel.org)
- f2fs: fix normal discard process (zhangdongdong1@oppo.com)
- f2fs: fix gc mode when gc_urgent_high_remaining is 1 (frank.li@vivo.com)
- f2fs: fix to invalidate dcc->f2fs_issue_discard in error path
  (chao@kernel.org)
- fortify: Do not cast to "unsigned char" (keescook@chromium.org)
- apparmor: Fix memleak in alloc_ns() (xiujianfeng@huawei.com)
- crypto: rockchip - rework by using crypto_engine (clabbe@baylibre.com)
- crypto: rockchip - remove non-aligned handling (clabbe@baylibre.com)
- crypto: rockchip - better handle cipher key (clabbe@baylibre.com)
- crypto: rockchip - add fallback for ahash (clabbe@baylibre.com)
- crypto: rockchip - add fallback for cipher (clabbe@baylibre.com)
- crypto: rockchip - do not store mode globally (clabbe@baylibre.com)
- crypto: rockchip - do not do custom power management (clabbe@baylibre.com)
- f2fs: Fix the race condition of resize flag between resizefs
  (zhangqilong3@huawei.com)
- PCI: pci-epf-test: Register notifier if only core_init_notifier is enabled
  (hayashi.kunihiko@socionext.com)
- RDMA/core: Fix order of nldev_exit call (leonro@nvidia.com)
- PCI: dwc: Fix n_fts[] array overrun (vidyas@nvidia.com)
- apparmor: Use pointer to struct aa_label for lbs_cred
  (xiujianfeng@huawei.com)
- scsi: core: Fix a race between scsi_done() and scsi_timeout()
  (bvanassche@acm.org)
- crypto: tcrypt - fix return value for multiple subtests (elliott@hpe.com)
- crypto: nitrox - avoid double free on error path in nitrox_sriov_init()
  (n.petrova@fintech.ru)
- crypto: sun8i-ss - use dma_addr instead u32 (clabbe@baylibre.com)
- crypto: hisilicon/qm - re-enable communicate interrupt before notifying PF
  (qianweili@huawei.com)
- crypto: hisilicon/qm - fix incorrect parameters usage (qianweili@huawei.com)
- apparmor: Fix regression in stacking due to label flags
  (john.johansen@canonical.com)
- apparmor: Fix abi check to include v8 abi (john.johansen@canonical.com)
- apparmor: fix lockdep warning when removing a namespace
  (john.johansen@canonical.com)
- apparmor: fix a memleak in multi_transaction_new() (cuigaosheng1@huawei.com)
- net: dsa: tag_8021q: avoid leaking ctx on dsa_tag_8021q_register() error path
  (vladimir.oltean@nxp.com)
- i40e: Fix the inability to attach XDP program on downed interface
  (bartoszx.staszewski@intel.com)
- stmmac: fix potential division by 0 (piergiorgio.beruto@gmail.com)
- octeontx2-af: cn10k: mcs: Fix a resource leak in the probe and remove
  functions (christophe.jaillet@wanadoo.fr)
- Bluetooth: RFCOMM: don't call kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- Bluetooth: hci_core: don't call kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- Bluetooth: hci_bcsp: don't call kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- Bluetooth: hci_h5: don't call kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- Bluetooth: hci_ll: don't call kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- Bluetooth: hci_qca: don't call kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- Bluetooth: btusb: don't call kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- Bluetooth: btintel: Fix missing free skb in btintel_setup_combined()
  (bobo.shaobowang@huawei.com)
- Bluetooth: hci_conn: Fix crash on hci_create_cis_sync
  (luiz.von.dentz@intel.com)
- Bluetooth: Fix EALREADY and ELOOP cases in bt_status()
  (christophe.jaillet@wanadoo.fr)
- Bluetooth: MGMT: Fix error report for ADD_EXT_ADV_PARAMS
  (inga.stotland@intel.com)
- Bluetooth: hci_core: fix error handling in hci_register_dev()
  (yangyingliang@huawei.com)
- sctp: sysctl: make extra pointers netns aware (firo.yang@suse.com)
- ntb_netdev: Use dev_kfree_skb_any() in interrupt context
  (epilmore@gigaio.com)
- net: lan9303: Fix read error execution path (jerry.ray@microchip.com)
- net: ethernet: ti: am65-cpsw: Fix PM runtime leakage in
  am65_cpsw_nuss_ndo_slave_open() (rogerq@kernel.org)
- can: tcan4x5x: Fix use of register error status mask (msp@baylibre.com)
- can: m_can: Call the RAM init directly from m_can_chip_config
  (vivek.2311@samsung.com)
- can: tcan4x5x: Remove invalid write in clear_interrupts (msp@baylibre.com)
- net: amd-xgbe: Check only the minimum speed for active/passive cables
  (thomas.lendacky@amd.com)
- net: amd-xgbe: Fix logic around active and passive cables
  (thomas.lendacky@amd.com)
- af_unix: call proto_unregister() in the error path in af_unix_init()
  (yangyingliang@huawei.com)
- net: setsockopt: fix IPV6_UNICAST_IF option for connected sockets
  (richardbgobert@gmail.com)
- net: amd: lance: don't call dev_kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- hamradio: don't call dev_kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- net: ethernet: dnet: don't call dev_kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- net: emaclite: don't call dev_kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- net: apple: bmac: don't call dev_kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- net: apple: mace: don't call dev_kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- net/tunnel: wait until all sk_user_data reader finish before releasing the
  sock (liuhangbin@gmail.com)
- net: farsync: Fix kmemleak when rmmods farsync (lizetao1@huawei.com)
- ethernet: s2io: don't call dev_kfree_skb() under spin_lock_irqsave()
  (yangyingliang@huawei.com)
- of: overlay: fix null pointer dereferencing in find_dup_cset_node_entry() and
  find_dup_cset_prop() (ruanjinjie@huawei.com)
- ipvs: use u64_stats_t for the per-cpu counters (ja@ssi.bg)
- drivers: net: qlcnic: Fix potential memory leak in qlcnic_sriov_init()
  (yuancan@huawei.com)
- net: stmmac: fix possible memory leak in stmmac_dvr_probe()
  (cuigaosheng1@huawei.com)
- net: stmmac: selftests: fix potential memleak in stmmac_test_arpoffload()
  (zhangchangzhong@huawei.com)
- net: defxx: Fix missing err handling in dfx_init()
  (liuyongqiang13@huawei.com)
- net: vmw_vsock: vmci: Check memcpy_from_msg() (artem.chernyshev@red-soft.ru)
- clk: socfpga: Fix memory leak in socfpga_gate_init() (xiujianfeng@huawei.com)
- bpf: Do not zero-extend kfunc return values (bjorn@rivosinc.com)
- blktrace: Fix output non-blktrace event when blk_classic option enabled
  (yangjihong1@huawei.com)
- wifi: brcmfmac: Fix error return code in brcmf_sdio_download_firmware()
  (wangyufen@huawei.com)
- wifi: rtl8xxxu: Fix the channel width reporting (rtl8821cerfe2@gmail.com)
- wifi: rtl8xxxu: Add __packed to struct rtl8723bu_c2h
  (rtl8821cerfe2@gmail.com)
- spi: spi-gpio: Don't set MOSI as an input if not 3WIRE mode
  (kris@embeddedTS.com)
- clk: samsung: Fix memory leak in _samsung_clk_register_pll()
  (xiujianfeng@huawei.com)
- media: staging: stkwebcam: Restore MEDIA_{USB,CAMERA}_SUPPORT dependencies
  (geert+renesas@glider.be)
- media: coda: Add check for kmalloc (jiasheng@iscas.ac.cn)
- media: coda: Add check for dcoda_iram_alloc (jiasheng@iscas.ac.cn)
- media: c8sectpfe: Add of_node_put() when breaking out of loop
  (windhl@126.com)
- regulator: qcom-labibb: Fix missing of_node_put() in
  qcom_labibb_regulator_probe() (yuancan@huawei.com)
- nvme: pass nr_maps explicitly to nvme_alloc_io_tag_set (hch@lst.de)
- mmc: core: Normalize the error handling branch in sd_read_ext_regs()
  (thunder.leizhen@huawei.com)
- memstick/ms_block: Add check for alloc_ordered_workqueue
  (jiasheng@iscas.ac.cn)
- mmc: renesas_sdhi: alway populate SCC pointer (wsa+renesas@sang-
  engineering.com)
- mmc: mmci: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: wbsd: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: via-sdmmc: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: meson-gx: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: omap_hsmmc: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: atmel-mci: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: litex_mmc: ensure `host->irq == 0` if polling (gsomlo@gmail.com)
- mmc: wmt-sdmmc: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: vub300: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: toshsd: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: rtsx_usb_sdmmc: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: rtsx_pci: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: pxamci: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: mxcmmc: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: moxart: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- mmc: alcor: fix return value check of mmc_add_host()
  (yangyingliang@huawei.com)
- hwmon: (emc2305) fix pwm never being able to set lower (nanpuyue@gmail.com)
- hwmon: (emc2305) fix unable to probe emc2301/2/3 (nanpuyue@gmail.com)
- bpftool: Fix memory leak in do_build_table_cb (linmq006@gmail.com)
- riscv, bpf: Emit fixed-length instructions for BPF_PSEUDO_FUNC
  (pulehui@huawei.com)
- NFSv4.x: Fail client initialisation if state manager thread can't run
  (trond.myklebust@hammerspace.com)
- NFS: Allow very small rsize & wsize again (Anna.Schumaker@Netapp.com)
- NFSv4.2: Set the correct size scratch buffer for decoding READ_PLUS
  (Anna.Schumaker@Netapp.com)
- SUNRPC: Fix missing release socket in rpc_sockname()
  (bobo.shaobowang@huawei.com)
- xprtrdma: Fix regbuf data not freed in rpcrdma_req_create()
  (zhangxiaoxu5@huawei.com)
- pinctrl: thunderbay: fix possible memory leak in thunderbay_build_functions()
  (cuigaosheng1@huawei.com)
- ALSA: mts64: fix possible null-ptr-defer in snd_mts64_interrupt
  (cuigaosheng1@huawei.com)
- media: ov5640: set correct default link frequency (guoniu.zhou@nxp.com)
- media: saa7164: fix missing pci_disable_device() (liushixin2@huawei.com)
- ALSA: pcm: Set missing stop_operating flag at undoing trigger start
  (tiwai@suse.de)
- bpf, sockmap: fix race in sock_map_free() (edumazet@google.com)
- bpf: Add dummy type reference to nf_conn___init to fix type deduplication
  (toke@redhat.com)
- hwmon: (jc42) Restore the min/max/critical temperatures on resume
  (martin.blumenstingl@googlemail.com)
- hwmon: (jc42) Convert register access and caching to regmap/regcache
  (martin.blumenstingl@googlemail.com)
- regulator: core: fix resource leak in regulator_register()
  (yangyingliang@huawei.com)
- configfs: fix possible memory leak in configfs_create_dir()
  (chenzhongjin@huawei.com)
- hsr: Synchronize sequence number updates. (bigeasy@linutronix.de)
- hsr: Synchronize sending frames to have always incremented outgoing seq nr.
  (bigeasy@linutronix.de)
- hsr: Disable netpoll. (bigeasy@linutronix.de)
- hsr: Avoid double remove of a node. (bigeasy@linutronix.de)
- hsr: Add a rcu-read lock to hsr_forward_skb(). (bigeasy@linutronix.de)
- Revert "net: hsr: use hlist_head instead of list_head for mac addresses"
  (bigeasy@linutronix.de)
- clk: qcom: clk-krait: fix wrong div2 functions (ansuelsmth@gmail.com)
- clk: qcom: lpass-sc7180: Fix pm_runtime usage (dianders@chromium.org)
- clk: qcom: lpass-sc7280: Fix pm_runtime usage (dianders@chromium.org)
- regulator: core: fix module refcount leak in set_supply()
  (yangyingliang@huawei.com)
- mt76: mt7915: Fix PCI device refcount leak in mt7915_pci_init_hif2()
  (wangxiongfeng2@huawei.com)
- wifi: mt76: do not send firmware FW_FEATURE_NON_DL region
  (deren.wu@mediatek.com)
- wifi: mt76: mt7921: Add missing __packed annotation of struct mt7921_clc
  (deren.wu@mediatek.com)
- wifi: mt76: fix coverity overrun-call in mt76_get_txpower()
  (deren.wu@mediatek.com)
- wifi: mt76: mt7921: fix wrong power after multiple SAR set
  (YN.Chen@mediatek.com)
- wifi: mt76: mt7915: Fix chainmask calculation on mt7915 DBDC
  (nicolas.cavallari@green-communications.fr)
- wifi: mt76: mt7915: rework eeprom tx paths and streams init
  (shayne.chen@mediatek.com)
- wifi: mt76: mt7921: fix reporting of TX AGGR histogram (lorenzo@kernel.org)
- wifi: mt76: mt7915: fix reporting of TX AGGR histogram (lorenzo@kernel.org)
- wifi: mt76: mt7915: fix mt7915_mac_set_timing() (ryder.lee@mediatek.com)
- wifi: mt76: mt7921: fix antenna signal are way off in monitor mode
  (sean.wang@mediatek.com)
- wifi: cfg80211: Fix not unregister reg_pdev when load_builtin_regdb_keys()
  fails (chenzhongjin@huawei.com)
- wifi: mac80211: fix maybe-unused warning (ihuguet@redhat.com)
- wifi: mac80211: fix memory leak in ieee80211_if_add()
  (shaozhengchao@huawei.com)
- wifi: nl80211: Add checks for nla_nest_start() in nl80211_send_iface()
  (yuancan@huawei.com)
- spi: spidev: mask SPI_CS_HIGH in SPI_IOC_RD_MODE
  (alexander.sverdlin@siemens.com)
- bonding: uninitialized variable in bond_miimon_inspect() (error27@gmail.com)
- bpf, sockmap: Fix data loss caused by using apply_bytes on ingress redirect
  (yangpc@wangsu.com)
- bpf, sockmap: Fix missing BPF_F_INGRESS flag when using apply_bytes
  (yangpc@wangsu.com)
- bpf, sockmap: Fix repeated calls to sock_put() when msg has more_data
  (yangpc@wangsu.com)
- Input: wistron_btns - disable on UML (rdunlap@infradead.org)
- netfilter: conntrack: set icmpv6 redirects as RELATED (fw@strlen.de)
- clk: visconti: Fix memory leak in visconti_register_pll()
  (xiujianfeng@huawei.com)
- ASoC: pcm512x: Fix PM disable depth imbalance in pcm512x_probe
  (zhangqilong3@huawei.com)
- drm/i915/bios: fix a memory leak in generate_lfp_data_ptrs
  (xiafukun@huawei.com)
- drm/amdkfd: Fix memory leakage (konstantin.meskhidze@huawei.com)
- drm/amdgpu: Fix PCI device refcount leak in amdgpu_atrm_get_bios()
  (wangxiongfeng2@huawei.com)
- drm/radeon: Fix PCI device refcount leak in radeon_atrm_get_bios()
  (wangxiongfeng2@huawei.com)
- amdgpu/nv.c: Corrected typo in the video capabilities resolution
  (veerabadhran.gopalakrishnan@amd.com)
- drm/amd/pm/smu11: BACO is supported when it's in BACO state
  (guchun.chen@amd.com)
- clk: mediatek: fix dependency of MT7986 ADC clocks (daniel@makrotopia.org)
- ASoC: mediatek: mt8173: Enable IRQ when pdata is ready (ribalda@chromium.org)
- wifi: iwlwifi: mvm: fix double free on tx path. (greearb@candelatech.com)
- wifi: rtl8xxxu: Fix use after rcu_read_unlock in rtl8xxxu_bss_info_changed
  (rtl8821cerfe2@gmail.com)
- wifi: plfxlc: fix potential memory leak in __lf_x_usb_enable_rx()
  (william.xuanziyang@huawei.com)
- ALSA: asihpi: fix missing pci_disable_device() (liushixin2@huawei.com)
- NFS: Fix an Oops in nfs_d_automount() (trond.myklebust@hammerspace.com)
- NFSv4: Fix a deadlock between nfs4_open_recover_helper() and delegreturn
  (trond.myklebust@hammerspace.com)
- NFSv4: Fix a credential leak in _nfs4_discover_trunking()
  (trond.myklebust@hammerspace.com)
- NFSv4.2: Fix initialisation of struct nfs4_label
  (trond.myklebust@hammerspace.com)
- NFSv4.2: Fix a memory stomp in decode_attr_security_label
  (trond.myklebust@hammerspace.com)
- NFSv4.2: Always decode the security label (trond.myklebust@hammerspace.com)
- NFSv4.2: Clear FATTR4_WORD2_SECURITY_LABEL when done decoding
  (trond.myklebust@hammerspace.com)
- drm/msm/mdp5: fix reading hw revision on db410c platform
  (dmitry.baryshkov@linaro.org)
- ASoC: mediatek: mtk-btcvsd: Add checks for write and read of mtk_btcvsd_snd
  (jiasheng@iscas.ac.cn)
- ASoC: dt-bindings: wcd9335: fix reset line polarity in example
  (dmitry.torokhov@gmail.com)
- drm/tegra: Add missing clk_disable_unprepare() in tegra_dc_probe()
  (zhangzekun11@huawei.com)
- media: s5p-mfc: Add variant data for MFC v7 hardware for Exynos 3250 SoC
  (aakarsh.jain@samsung.com)
- media: mediatek: vcodec: Core thread depends on core_list
  (yunfei.dong@mediatek.com)
- media: mediatek: vcodec: Setting lat buf to lat_list when lat decode error
  (yunfei.dong@mediatek.com)
- media: mediatek: vcodec: Fix h264 set lat buffer error
  (yunfei.dong@mediatek.com)
- media: mediatek: vcodec: Fix getting NULL pointer for dst buffer
  (yunfei.dong@mediatek.com)
- media: amphion: lock and check m2m_ctx in event handler (ming.qian@nxp.com)
- media: amphion: cancel vpu before release instance (ming.qian@nxp.com)
- media: amphion: try to wakeup vpu core to avoid failure (ming.qian@nxp.com)
- media: sun8i-a83t-mipi-csi2: Register async subdev with no sensor attached
  (paul.kocialkowski@bootlin.com)
- media: sun6i-mipi-csi2: Register async subdev with no sensor attached
  (paul.kocialkowski@bootlin.com)
- media: sun8i-a83t-mipi-csi2: Require both pads to be connected for streaming
  (paul.kocialkowski@bootlin.com)
- media: sun6i-mipi-csi2: Require both pads to be connected for streaming
  (paul.kocialkowski@bootlin.com)
- x86/boot: Skip realmode init code when running as Xen PV guest
  (jgross@suse.com)
- media: dvb-usb: az6027: fix null-ptr-deref in az6027_i2c_xfer()
  (zhongbaisong@huawei.com)
- media: dvb-core: Fix ignored return value in dvb_register_frontend()
  (chenzhongjin@huawei.com)
- pinctrl: pinconf-generic: add missing of_node_put() (zhangpeng362@huawei.com)
- clk: imx8mn: fix imx8mn_enet_phy_sels clocks list
  (dario.binacchi@amarulasolutions.com)
- clk: imx8mn: fix imx8mn_sai2_sels clocks list
  (dario.binacchi@amarulasolutions.com)
- clk: imx: rename video_pll1 to video_pll
  (dario.binacchi@amarulasolutions.com)
- clk: imx: replace osc_hdmi with dummy (dario.binacchi@amarulasolutions.com)
- clk: imx8mn: rename vpu_pll to m7_alt_pll
  (dario.binacchi@amarulasolutions.com)
- media: mt9p031: Drop bogus v4l2_subdev_get_try_crop() call from
  mt9p031_init_cfg() (marex@denx.de)
- media: imx: imx7-media-csi: Clear BIT_MIPI_DOUBLE_CMPNT for <16b formats
  (laurent.pinchart@ideasonboard.com)
- media: imon: fix a race condition in send_packet()
  (gautammenghani201@gmail.com)
- media: vimc: Fix wrong function called when vimc_init() fails
  (chenzhongjin@huawei.com)
- ASoC: mediatek: mt8186: Correct I2S shared clocks (jiaxin.yu@mediatek.com)
- ASoC: qcom: cleanup and fix dependency of QCOM_COMMON
  (srinivas.kandagatla@linaro.org)
- ASoC: qcom: Add checks for devm_kcalloc (yuancan@huawei.com)
- drbd: destroy workqueue when drbd device was freed
  (bobo.shaobowang@huawei.com)
- drbd: remove call to memset before free device/resource/connection
  (bobo.shaobowang@huawei.com)
- mtd: maps: pxa2xx-flash: fix memory leak in probe (zhengyongjun3@huawei.com)
- mtd: core: Fix refcount error in del_mtd_device() (shangxiaojing@huawei.com)
- clk: microchip: check for null return of devm_kzalloc()
  (tanghui20@huawei.com)
- bonding: fix link recovery in mode 2 when updelay is nonzero
  (jtoppins@redhat.com)
- selftests/bpf: Mount debugfs in setns_by_fd (sdf@google.com)
- selftests/bpf: Make sure zero-len skbs aren't redirectable (sdf@google.com)
- drm/i915/guc: make default_lists const data (jani.nikula@intel.com)
- drm/amdgpu: fix pci device refcount leak (yangyingliang@huawei.com)
- clk: rockchip: Fix memory leak in rockchip_clk_register_pll()
  (xiujianfeng@huawei.com)
- regulator: core: use kfree_const() to free space conditionally
  (bobo.shaobowang@huawei.com)
- ALSA: seq: fix undefined behavior in bit shift for SNDRV_SEQ_FILTER_USE_EVENT
  (zhongbaisong@huawei.com)
- ALSA: pcm: fix undefined behavior in bit shift for SNDRV_PCM_RATE_KNOT
  (zhongbaisong@huawei.com)
- ASoC: Intel: avs: Lock substream before snd_pcm_stop()
  (cezary.rojewski@intel.com)
- ASoC: Intel: Skylake: Fix Kconfig dependency (lili.li@intel.com)
- wifi: rtw89: fix physts IE page check (kevin_yang@realtek.com)
- pinctrl: k210: call of_node_put() (zhangpeng362@huawei.com)
- clk: imx: imxrt1050: fix IMXRT1050_CLK_LCDIF_APB offsets
  (giulio.benetti@benettiengineering.com)
- HID: hid-sensor-custom: set fixed size for custom attributes
  (marcus.folkesson@gmail.com)
- bpf: Move skb->len == 0 checks into __bpf_redirect (sdf@google.com)
- clk: imx93: correct enet clock (peng.fan@nxp.com)
- clk: imx93: unmap anatop base in error handling path (peng.fan@nxp.com)
- HID: i2c: let RMI devices decide what constitutes wakeup event
  (dmitry.torokhov@gmail.com)
- bpf: Pin the start cgroup in cgroup_iter_seq_init() (houtao1@huawei.com)
- clk: imx93: correct the flexspi1 clock setting (haibo.chen@nxp.com)
- mtd: spi-nor: Fix the number of bytes for the dummy cycles (allen-
  kh.cheng@mediatek.com)
- mtd: spi-nor: hide jedec_id sysfs attribute if not present (michael@walle.cc)
- net: Return errno in sk->sk_prot->get_port(). (kuniyu@amazon.com)
- udp: Clean up some functions. (kuniyu@amazon.com)
- net: ethernet: mtk_eth_soc: fix RSTCTRL_PPE{0,1} definitions
  (lorenzo@kernel.org)
- media: videobuf-dma-contig: use dma_mmap_coherent (hch@lst.de)
- media: amphion: Fix error handling in vpu_driver_init() (yuancan@huawei.com)
- media: platform: exynos4-is: Fix error handling in fimc_md_init()
  (yuancan@huawei.com)
- media: solo6x10: fix possible memory leak in solo_sysfs_init()
  (yangyingliang@huawei.com)
- media: vidtv: Fix use-after-free in vidtv_bridge_dvb_init()
  (chenzhongjin@huawei.com)
- media: amphion: apply vb2_queue_error instead of setting manually
  (ming.qian@nxp.com)
- media: amphion: add lock around vdec_g_fmt (ming.qian@nxp.com)
- net: ethernet: mtk_eth_soc: do not overwrite mtu configuration running reset
  routine (lorenzo@kernel.org)
- ASoC: amd: acp: Fix possible UAF in acp_dma_open (cuigaosheng1@huawei.com)
- Input: elants_i2c - properly handle the reset GPIO when power is off
  (dianders@chromium.org)
- mtd: lpddr2_nvm: Fix possible null-ptr-deref (tanghui20@huawei.com)
- drm/msm/a6xx: Fix speed-bin detection vs probe-defer (robdclark@chromium.org)
- wifi: ath10k: Fix return value in ath10k_pci_init() (xiujianfeng@huawei.com)
- selftests/bpf: fix memory leak of lsm_cgroup (wangyufen@huawei.com)
- dm: track per-add_disk holder relations in DM (hch@lst.de)
- dm: make sure create and remove dm device won't race with open and close
  table (yukuai3@huawei.com)
- dm: cleanup close_table_device (hch@lst.de)
- dm: cleanup open_table_device (hch@lst.de)
- block: clear ->slave_dir when dropping the main slave_dir reference
  (hch@lst.de)
- ima: Fix misuse of dereference of pointer in template_desc_init_fields()
  (xiujianfeng@huawei.com)
- integrity: Fix memory leakage in keyring allocation error path
  (guozihua@huawei.com)
- ALSA: memalloc: Allocate more contiguous pages for fallback case
  (tiwai@suse.de)
- drm/fourcc: Fix vsub/hsub for Q410 and Q401 (brian.starkey@arm.com)
- regulator: qcom-rpmh: Fix PMR735a S3 regulator spec
  (konrad.dybcio@linaro.org)
- wifi: rtw89: Fix some error handling path in rtw89_core_sta_assoc()
  (christophe.jaillet@wanadoo.fr)
- nvme: return err on nvme_init_non_mdts_limits fail (j.granados@samsung.com)
- amdgpu/pm: prevent array underflow in vega20_odn_edit_dpm_table()
  (error27@gmail.com)
- regulator: core: fix unbalanced of node refcount in regulator_dev_lookup()
  (yangyingliang@huawei.com)
- nvmet: only allocate a single slab for bvecs (hch@lst.de)
- ASoC: pxa: fix null-pointer dereference in filter() (zengheng4@huawei.com)
- drm/mediatek: Modify dpi power on/off sequence. (xinlei.lee@mediatek.com)
- selftests/bpf: Fix incorrect ASSERT in the tcp_hdr_options test
  (martin.lau@kernel.org)
- selftests/bpf: Fix xdp_synproxy compilation failure in 32-bit arch
  (yangjihong1@huawei.com)
- ASoC: codecs: wsa883x: use correct header file (rdunlap@infradead.org)
- ASoC: codecs: wsa883x: Use proper shutdown GPIO polarity
  (krzysztof.kozlowski@linaro.org)
- module: Fix NULL vs IS_ERR checking for module_get_next_page
  (linmq006@gmail.com)
- wifi: iwlwifi: mei: fix potential NULL-ptr deref after clone
  (johannes.berg@intel.com)
- wifi: iwlwifi: mei: avoid blocking sap messages handling due to rtnl lock
  (avraham.stern@intel.com)
- wifi: iwlwifi: mei: fix tx DHCP packet for devices with new Tx API
  (emmanuel.grumbach@intel.com)
- wifi: iwlwifi: mei: don't send SAP commands if AMT is disabled
  (emmanuel.grumbach@intel.com)
- wifi: iwlwifi: mei: make sure ownership confirmed message is sent
  (avraham.stern@intel.com)
- pinctrl: mediatek: fix the pinconf register offset of some pins
  (sam.shih@mediatek.com)
- dt-bindings: pinctrl: update uart/mmc bindings for MT7986 SoC
  (frank-w@public-files.de)
- drm/radeon: Add the missed acpi_put_table() to fix memory leak
  (guohanjun@huawei.com)
- bfq: fix waker_bfqq inconsistency crash (khazhy@chromium.org)
- drbd: use blk_queue_max_discard_sectors helper
  (christoph.boehmwalder@linbit.com)
- regmap-irq: Use the new num_config_regs property in
  regmap_add_irq_chip_fwnode (y.oudjana@protonmail.com)
- drm: rcar-du: Drop leftovers dependencies from Kconfig
  (laurent.pinchart+renesas@ideasonboard.com)
- wifi: rtw89: use u32_encode_bits() to fill MAC quota value
  (pkshih@realtek.com)
- drm: lcdif: Set and enable FIFO Panic threshold (marex@denx.de)
- rxrpc: Fix ack.bufferSize to be 0 when generating an ack
  (dhowells@redhat.com)
- net, proc: Provide PROC_FS=n fallback for proc_create_net_single_write()
  (dhowells@redhat.com)
- virt/sev-guest: Add a MODULE_ALIAS (crobinso@redhat.com)
- clk: renesas: r8a779f0: Fix SCIF parent clocks (wsa+renesas@sang-
  engineering.com)
- clk: renesas: r8a779f0: Fix HSCIF parent clocks (wsa+renesas@sang-
  engineering.com)
- media: camss: Do not attach an already attached power domain on MSM8916
  platform (vladimir.zapolskiy@linaro.org)
- media: camss: Clean up received buffers on failed start of streaming
  (vladimir.zapolskiy@linaro.org)
- wifi: rsi: Fix handling of 802.3 EAPOL frames sent via control port
  (marex@denx.de)
- Input: joystick - fix Kconfig warning for JOYSTICK_ADC
  (rdunlap@infradead.org)
- mtd: core: fix possible resource leak in init_mtd() (cuigaosheng1@huawei.com)
- mtd: Fix device name leak when register device failed in add_mtd_device()
  (zhangxiaoxu5@huawei.com)
- clk: qcom: gcc-sm8250: Use retention mode for USB GDSCs
  (manivannan.sadhasivam@linaro.org)
- clk: qcom: dispcc-sm6350: Add CLK_OPS_PARENT_ENABLE to pixel&byte src
  (konrad.dybcio@somainline.org)
- clk: qcom: gcc-ipq806x: use parent_data for the last remaining entry
  (dmitry.baryshkov@linaro.org)
- bpf: propagate precision across all frames, not just the last one
  (andrii@kernel.org)
- bpf: propagate precision in ALU/ALU64 operations (andrii@kernel.org)
- media: platform: exynos4-is: fix return value check in fimc_md_probe()
  (yangyingliang@huawei.com)
- media: vivid: fix compose size exceed boundary (liushixin2@huawei.com)
- media: rkvdec: Add required padding (andrzej.p@collabora.com)
- media: platform: mtk-mdp3: fix error handling in mdp_probe()
  (moudy.ho@mediatek.com)
- media: platform: mtk-mdp3: fix error handling about components clock_on
  (moudy.ho@mediatek.com)
- media: platform: mtk-mdp3: fix error handling in mdp_cmdq_send()
  (moudy.ho@mediatek.com)
- drm/msm/dsi: Prevent signed BPG offsets from bleeding into adjacent bits
  (marijn.suijten@somainline.org)
- drm/msm/dsi: Disallow 8 BPC DSC configuration for alternative BPC values
  (marijn.suijten@somainline.org)
- drm/msm/dsi: Account for DSC's bits_per_pixel having 4 fractional bits
  (marijn.suijten@somainline.org)
- drm/msm/dsi: Migrate to drm_dsc_compute_rc_parameters()
  (marijn.suijten@somainline.org)
- drm/msm/dsi: Appropriately set dsc->mux_word_size based on bpc
  (marijn.suijten@somainline.org)
- drm/msm/dsi: Reuse earlier computed dsc->slice_chunk_size
  (marijn.suijten@somainline.org)
- drm/msm/dsi: Use DIV_ROUND_UP instead of conditional increment on modulo
  (marijn.suijten@somainline.org)
- drm/msm/dsi: Remove repeated calculation of slice_per_intf
  (marijn.suijten@somainline.org)
- drm/msm/dsi: Remove useless math in DSC calculations
  (marijn.suijten@somainline.org)
- drm/msm/dpu1: Account for DSC's bits_per_pixel having 4 fractional bits
  (marijn.suijten@somainline.org)
- bpf: Fix slot type check in check_stack_write_var_off (memxor@gmail.com)
- bpf: Clobber stack slot when writing over spilled PTR_TO_BTF_ID
  (memxor@gmail.com)
- drm/msm/hdmi: use devres helper for runtime PM management
  (dmitry.baryshkov@linaro.org)
- ima: Handle -ESTALE returned by ima_filter_rule_match() (guozihua@huawei.com)
- drm/msm/mdp5: stop overriding drvdata (dmitry.baryshkov@linaro.org)
- drm/ttm: fix undefined behavior in bit shift for TTM_TT_FLAG_PRIV_POPULATED
  (cuigaosheng1@huawei.com)
- drm/panel/panel-sitronix-st7701: Remove panel on DSI attach failure
  (marex@denx.de)
- spi: Update reference to struct spi_controller (j.neuschaefer@gmx.net)
- drm/panel/panel-sitronix-st7701: Fix RTNI calculation (marex@denx.de)
- drm: lcdif: change burst size to 256B (m.felsch@pengutronix.de)
- clk: renesas: r9a06g032: Repair grave increment error (marex@denx.de)
- drm/i915/dgfx: Grab wakeref at i915_ttm_unmap_virtual
  (anshuman.gupta@intel.com)
- drm/i915: Encapsulate lmem rpm stuff in intel_runtime_pm
  (anshuman.gupta@intel.com)
- drm/i915: Refactor ttm ghost obj detection (nirmoy.das@intel.com)
- drm/i915: Handle all GTs on driver (un)load paths (tvrtko.ursulin@intel.com)
- drm/rockchip: lvds: fix PM usage counter unbalance in poweron
  (zhangqilong3@huawei.com)
- drm/amd/display: wait for vblank during pipe programming (Haiyi.Zhou@amd.com)
- dw9768: Enable low-power probe on ACPI (sakari.ailus@linux.intel.com)
- drm/i915/guc: Fix GuC error capture sizing estimation and reporting
  (alan.previn.teres.alexis@intel.com)
- drm/i915/guc: Add error-capture init warnings when needed
  (alan.previn.teres.alexis@intel.com)
- ASoC: dt-bindings: rt5682: Set sound-dai-cells to 1 (nfraprado@collabora.com)
- clk: renesas: r8a779a0: Fix SD0H clock name (wsa+renesas@sang-
  engineering.com)
- clk: renesas: r8a779f0: Fix SD0H clock name (geert+renesas@glider.be)
- can: kvaser_usb: Compare requested bittiming parameters with actual
  parameters in do_set_{,data}_bittiming (extja@kvaser.com)
- can: kvaser_usb: Add struct kvaser_usb_busparams (extja@kvaser.com)
- can: kvaser_usb_leaf: Fix bogus restart events (anssi.hannula@bitwise.fi)
- can: kvaser_usb_leaf: Fix wrong CAN state after stopping
  (anssi.hannula@bitwise.fi)
- can: kvaser_usb_leaf: Fix improved state not being reported
  (anssi.hannula@bitwise.fi)
- can: kvaser_usb_leaf: Set Warning state even without bus errors
  (anssi.hannula@bitwise.fi)
- can: kvaser_usb: kvaser_usb_leaf: Handle CMD_ERROR_EVENT (extja@kvaser.com)
- can: kvaser_usb: kvaser_usb_leaf: Rename {leaf,usbcan}_cmd_error_event to
  {leaf,usbcan}_cmd_can_error_event (extja@kvaser.com)
- can: kvaser_usb: kvaser_usb_leaf: Get capabilities from device
  (extja@kvaser.com)
- libbpf: Btf dedup identical struct test needs check for nested structs/arrays
  (alan.maguire@oracle.com)
- media: exynos4-is: don't rely on the v4l2_async_subdev internals
  (m.szyprowski@samsung.com)
- media: i2c: ov5648: Free V4L2 fwnode data on unbind (rafaelmendsr@gmail.com)
- soreuseport: Fix socket selection for SO_INCOMING_CPU. (kuniyu@amazon.com)
- venus: pm_helpers: Fix error check in vcodec_domains_get()
  (tangbin@cmss.chinamobile.com)
- media: i2c: ad5820: Fix error path (ribalda@chromium.org)
- media: i2c: hi846: Fix memory leak in hi846_parse_dt()
  (rafaelmendsr@gmail.com)
- drm/i915: Fix compute pre-emption w/a to apply to compute engines
  (John.C.Harrison@Intel.com)
- drm/i915/guc: Limit scheduling properties to avoid overflow
  (John.C.Harrison@Intel.com)
- media: mediatek: vcodec: fix h264 cavlc bitstream fail
  (yunfei.dong@mediatek.com)
- media: cedrus: hevc: Fix offset adjustments (jernej.skrabec@gmail.com)
- media: v4l2-ioctl.c: Unify YCbCr/YUV terms in format descriptions
  (jernej.skrabec@gmail.com)
- media: adv748x: afe: Select input port when initializing AFE
  (niklas.soderlund+renesas@ragnatech.se)
- media: amphion: reset instance if it's aborted before codec header parsed
  (ming.qian@nxp.com)
- media: coda: jpeg: Add check for kmalloc (jiasheng@iscas.ac.cn)
- media: v4l2-ctrls: Fix off-by-one error in integer menu control check
  (laurent.pinchart+renesas@ideasonboard.com)
- Input: iqs7222 - protect against undefined slider size (jeff@labundy.com)
- drm/bridge: it6505: Initialize AUX channel in it6505_i2c_probe
  (treapking@chromium.org)
- selftests/bpf: fix missing BPF object files (wangyufen@huawei.com)
- samples/bpf: Fix MAC address swapping in xdp2_kern (gerhard@engleder-
  embedded.com)
- samples/bpf: Fix map iteration in xdp1_user (gerhard@engleder-embedded.com)
- net: ethernet: adi: adin1110: Fix SPI transfers
  (alexandru.tachici@analog.com)
- drm/amdgpu/powerplay/psm: Fix memory leak in power state init
  (rafaelmendsr@gmail.com)
- drm/amdgpu: Revert "drm/amdgpu: getting fan speed pwm for vega10 properly"
  (Asher.Song@amd.com)
- ipmi: kcs: Poll OBF briefly to reduce OBE latency (andrew@aj.id.au)
- ASoC: Intel: avs: Fix potential RX buffer overflow
  (cezary.rojewski@intel.com)
- ASoC: Intel: avs: Fix DMA mask assignment (cezary.rojewski@intel.com)
- pinctrl: ocelot: add missing destroy_workqueue() in error path in
  ocelot_pinctrl_probe() (yangyingliang@huawei.com)
- ata: libata: fix NCQ autosense logic (niklas.cassel@wdc.com)
- drm: lcdif: Switch to limited range for RGB to YUV conversion
  (laurent.pinchart@ideasonboard.com)
- libbpf: Fix null-pointer dereference in find_prog_by_sec_insn() (shung-
  hsi.yu@suse.com)
- libbpf: Deal with section with no data gracefully (shung-hsi.yu@suse.com)
- libbpf: Use elf_getshdrnum() instead of e_shnum (shung-hsi.yu@suse.com)
- selftest/bpf: Fix error usage of ASSERT_OK in xdp_adjust_tail.c
  (xukuohai@huawei.com)
- selftests/bpf: Fix error failure of case test_xdp_adjust_tail_grow
  (xukuohai@huawei.com)
- selftest/bpf: Fix memory leak in kprobe_multi_test (xukuohai@huawei.com)
- selftests/bpf: Fix memory leak caused by not destroying skeleton
  (xukuohai@huawei.com)
- libbpf: Fix memory leak in parse_usdt_arg() (xukuohai@huawei.com)
- libbpf: Fix use-after-free in btf_dump_name_dups (xukuohai@huawei.com)
- drm/bridge: adv7533: remove dynamic lane switching from adv7533 bridge
  (quic_abhinavk@quicinc.com)
- wifi: ath11k: fix firmware assert during bandwidth change for peer sta
  (quic_adisi@quicinc.com)
- wifi: rtl8xxxu: Fix reading the vendor of combo chips
  (rtl8821cerfe2@gmail.com)
- wifi: ath9k: hif_usb: Fix use-after-free in ath9k_hif_usb_reg_in_cb()
  (pchelkin@ispras.ru)
- wifi: ath9k: hif_usb: fix memory leak of urbs in
  ath9k_hif_usb_dealloc_tx_urbs() (pchelkin@ispras.ru)
- drm/atomic-helper: Don't allocate new plane state in CRTC check
  (tzimmermann@suse.de)
- wifi: mac80211: fix ifdef symbol name (johannes.berg@intel.com)
- wifi: mac80211: check link ID in auth/assoc continuation
  (johannes.berg@intel.com)
- wifi: mac80211: mlme: fix null-ptr deref on failed assoc
  (johannes.berg@intel.com)
- wifi: fix multi-link element subelement iteration (johannes.berg@intel.com)
- selftests/bpf: Add missing bpf_iter_vma_offset__destroy call
  (jolsa@kernel.org)
- platform/mellanox: mlxbf-pmc: Fix event typo (jahurley@nvidia.com)
- ipc: fix memory leak in init_mqueue_fs() (shaozhengchao@huawei.com)
- rapidio: devices: fix missing put_device in mport_cdev_open
  (caixinchen1@huawei.com)
- hfs: Fix OOB Write in hfs_asc2mac (zhangpeng362@huawei.com)
- relay: fix type mismatch when allocating memory in relay_create_buf()
  (Ilia.Gavrilov@infotecs.ru)
- eventfd: change int to __u64 in eventfd_signal() ifndef CONFIG_EVENTFD
  (zhangqilong3@huawei.com)
- rapidio: fix possible UAF when kfifo_alloc() fails (wangweiyang2@huawei.com)
- fs: sysv: Fix sysv_nblocks() returns wrong value (chenzhongjin@huawei.com)
- NFSD: pass range end to vfs_fsync_range() instead of count
  (bfoster@redhat.com)
- nfsd: return error if nfs4_setacl fails (jlayton@kernel.org)
- lockd: set other missing fields when unlocking files
  (trond.myklebust@hammerspace.com)
- MIPS: OCTEON: warn only once if deprecated link status is being used
  (ladis@linux-mips.org)
- MIPS: BCM63xx: Add check for NULL for clk in clk_enable
  (abelova@astralinux.ru)
- platform/x86: intel_scu_ipc: fix possible name leak in
  __intel_scu_ipc_register() (yangyingliang@huawei.com)
- platform/x86: mxm-wmi: fix memleak in mxm_wmi_call_mx[ds|mx]()
  (liaoyu15@huawei.com)
- platform/chrome: cros_ec_typec: zero out stale pointers
  (victording@chromium.org)
- erofs: validate the extent length for uncompressed pclusters
  (hsiangkao@linux.alibaba.com)
- erofs: fix missing unmap if z_erofs_get_extent_compressedlen() fails
  (hsiangkao@linux.alibaba.com)
- erofs: Fix pcluster memleak when its block address is zero
  (chenzhongjin@huawei.com)
- erofs: check the uniqueness of fsid in shared domain in advance
  (houtao1@huawei.com)
- PM: runtime: Do not call __rpm_callback() from rpm_idle()
  (rafael.j.wysocki@intel.com)
- xen/privcmd: Fix a possible warning in privcmd_ioctl_mmap_resource()
  (harshit.m.mogalapalli@oracle.com)
- x86/xen: Fix memory leak in xen_init_lock_cpu() (xiujianfeng@huawei.com)
- x86/xen: Fix memory leak in xen_smp_intr_init{_pv}() (xiujianfeng@huawei.com)
- uprobes/x86: Allow to probe a NOP instruction with 0x66 prefix
  (oleg@redhat.com)
- ACPICA: Fix use-after-free in acpi_ut_copy_ipackage_to_ipackage()
  (lizetao1@huawei.com)
- clocksource/drivers/timer-ti-dm: Fix missing clk_disable_unprepare in
  dmtimer_systimer_init_clock() (yangyingliang@huawei.com)
- clocksource/drivers/timer-ti-dm: Fix warning for omap_timer_match
  (tony@atomide.com)
- cpu/hotplug: Do not bail-out in DYING/STARTING sections
  (vdonnefort@google.com)
- cpu/hotplug: Make target_store() a nop when target == state
  (pauld@redhat.com)
- futex: Resend potentially swallowed owner death notification
  (izbyshev@ispras.ru)
- clocksource/drivers/sh_cmt: Access registers according to spec
  (wsa+renesas@sang-engineering.com)
- rapidio: rio: fix possible name leak in rio_register_mport()
  (yangyingliang@huawei.com)
- rapidio: fix possible name leaks when rio_add_device() fails
  (yangyingliang@huawei.com)
- ocfs2: fix memory leak in ocfs2_mount_volume() (ocfs2-devel@oss.oracle.com)
- debugfs: fix error when writing negative value to atomic_t debugfs file
  (akinobu.mita@gmail.com)
- lib/notifier-error-inject: fix error when writing -errno to debugfs file
  (akinobu.mita@gmail.com)
- libfs: add DEFINE_SIMPLE_ATTRIBUTE_SIGNED for signed value
  (akinobu.mita@gmail.com)
- cpufreq: amd_freq_sensitivity: Add missing pci_dev_put()
  (wangxiongfeng2@huawei.com)
- genirq/irqdesc: Don't try to remove non-existing sysfs files
  (yangyingliang@huawei.com)
- nfsd: don't call nfsd_file_put from client states seqfile display
  (jlayton@kernel.org)
- NFSD: Finish converting the NFSv3 GETACL result encoder
  (chuck.lever@oracle.com)
- NFSD: Finish converting the NFSv2 GETACL result encoder
  (chuck.lever@oracle.com)
- EDAC/i10nm: fix refcount leak in pci_get_dev_wrapper()
  (yangyingliang@huawei.com)
- irqchip/loongson-liointc: Fix improper error handling in liointc_init()
  (liupeibao@loongson.cn)
- irqchip/wpcm450: Fix memory leak in wpcm450_aic_of_init()
  (weiyongjun1@huawei.com)
- irqchip: gic-pm: Use pm_runtime_resume_and_get() in gic_probe()
  (shangxiaojing@huawei.com)
- irqchip/loongson-pch-pic: Fix translate callback for DT path
  (lvjianmin@loongson.cn)
- thermal: core: fix some possible name leaks in error paths
  (yangyingliang@huawei.com)
- platform/chrome: cros_usbpd_notify: Fix error handling in
  cros_usbpd_notify_init() (yuancan@huawei.com)
- perf/x86/intel/uncore: Fix reference count leak in __uncore_imc_init_box()
  (wangxiongfeng2@huawei.com)
- perf/x86/intel/uncore: Fix reference count leak in snr_uncore_mmio_map()
  (wangxiongfeng2@huawei.com)
- perf/x86/intel/uncore: Fix reference count leak in hswep_has_limit_sbox()
  (wangxiongfeng2@huawei.com)
- perf/x86/intel/uncore: Fix reference count leak in sad_cfg_iio_topology()
  (wangxiongfeng2@huawei.com)
- ACPI: pfr_update: use ACPI_FREE() to free acpi_object
  (bobo.shaobowang@huawei.com)
- ACPI: pfr_telemetry: use ACPI_FREE() to free acpi_object
  (bobo.shaobowang@huawei.com)
- mailbox: pcc: Reset pcc_chan_count to zero in case of PCC probe failure
  (lihuisong@huawei.com)
- PNP: fix name memory leak in pnp_alloc_dev() (yangyingliang@huawei.com)
- selftests/efivarfs: Add checking of the test return value
  (zhaogongyi@huawei.com)
- MIPS: vpe-cmp: fix possible memory leak while module exiting
  (yangyingliang@huawei.com)
- MIPS: vpe-mt: fix possible memory leak while module exiting
  (yangyingliang@huawei.com)
- cpufreq: qcom-hw: Fix the frequency returned by cpufreq_driver->get()
  (manivannan.sadhasivam@linaro.org)
- selftests: cgroup: fix unsigned comparison with less than zero
  (yuehaibing@huawei.com)
- ocfs2: fix memory leak in ocfs2_stack_glue_init() (shangxiaojing@huawei.com)
- lib/fonts: fix undefined behavior in bit shift for get_default_font
  (cuigaosheng1@huawei.com)
- proc: fixup uptime selftest (adobriyan@gmail.com)
- timerqueue: Use rb_entry_safe() in timerqueue_getnext()
  (pobrn@protonmail.com)
- platform/x86: huawei-wmi: fix return value calculation (pobrn@protonmail.com)
- lib/debugobjects: fix stat count and optimize debug_objects_mem_init
  (wuchi.zero@gmail.com)
- perf: Fix possible memleak in pmu_dev_alloc() (chenzhongjin@huawei.com)
- selftests/ftrace: event_triggers: wait longer for test_event_enable
  (zouyipeng@huawei.com)
- ACPI: irq: Fix some kernel-doc issues (wangxiongfeng2@huawei.com)
- x86/split_lock: Add sysctl to control the misery mode (gpiccoli@igalia.com)
- cpufreq: qcom-hw: Fix memory leak in qcom_cpufreq_hw_read_lut()
  (judy.chenhui@huawei.com)
- fs: don't audit the capability check in simple_xattr_list()
  (omosnace@redhat.com)
- PM: hibernate: Fix mistake in kerneldoc comment (xiongxin@kylinos.cn)
- x86/sgx: Reduce delay and interference of enclave release
  (reinette.chatre@intel.com)
- sched/psi: Fix possible missing or delayed pending event
  (haolee.swjtu@gmail.com)
- alpha: fix syscall entry in !AUDUT_SYSCALL case (viro@zeniv.linux.org.uk)
- alpha: fix TIF_NOTIFY_SIGNAL handling (viro@zeniv.linux.org.uk)
- cpuidle: dt: Return the correct numbers of parsed idle states
  (ulf.hansson@linaro.org)
- sched/uclamp: Cater for uclamp in find_energy_efficient_cpu()'s early exit
  condition (qais.yousef@arm.com)
- sched/uclamp: Make cpu_overutilized() use util_fits_cpu()
  (qais.yousef@arm.com)
- sched/uclamp: Make asym_fits_capacity() use util_fits_cpu()
  (qais.yousef@arm.com)
- sched/uclamp: Make select_idle_capacity() use util_fits_cpu()
  (qais.yousef@arm.com)
- sched/uclamp: Fix fits_capacity() check in feec() (qais.yousef@arm.com)
- sched/uclamp: Make task_fits_capacity() use util_fits_cpu()
  (qais.yousef@arm.com)
- sched/uclamp: Fix relationship between uclamp and migration margin
  (qais.yousef@arm.com)
- ovl: remove privs in ovl_fallocate() (amir73il@gmail.com)
- ovl: remove privs in ovl_copyfile() (amir73il@gmail.com)
- tpm/tpm_crb: Fix error message in __crb_relinquish_locality()
  (mikelley@microsoft.com)
- tpm/tpm_ftpm_tee: Fix error handling in ftpm_mod_init() (yuancan@huawei.com)
- tpm: Add flag to use default cancellation policy (eajames@linux.ibm.com)
- tpm: tis_i2c: Fix sanity check interrupt enable mask (eajames@linux.ibm.com)
- arch: arm64: apple: t8103: Use standard "iommu" node name (j@jannau.net)
- pstore: Avoid kcore oops by vmap()ing with VM_IOREMAP (swboyd@chromium.org)
- ARM: mmp: fix timer_read delay (doug@schmorgal.com)
- pstore/ram: Fix error return code in ramoops_probe() (wangyufen@huawei.com)
- seccomp: Move copy_seccomp() to no failure path. (kuniyu@amazon.com)
- drivers/perf: hisi: Fix some event id for hisi-pcie-pmu
  (yangyicong@hisilicon.com)
- soc: apple: rtkit: Stop casting function pointer signatures
  (sven@svenpeter.dev)
- soc: apple: sart: Stop casting function pointer signatures
  (sven@svenpeter.dev)
- arm64: dts: armada-3720-turris-mox: Add missing interrupt for RTC
  (pali@kernel.org)
- ARM: dts: turris-omnia: Add switch port 6 node (pali@kernel.org)
- ARM: dts: turris-omnia: Add ethernet aliases (pali@kernel.org)
- ARM: dts: armada-39x: Fix assigned-addresses for every PCIe Root Port
  (pali@kernel.org)
- ARM: dts: armada-38x: Fix assigned-addresses for every PCIe Root Port
  (pali@kernel.org)
- ARM: dts: armada-375: Fix assigned-addresses for every PCIe Root Port
  (pali@kernel.org)
- ARM: dts: armada-xp: Fix assigned-addresses for every PCIe Root Port
  (pali@kernel.org)
- ARM: dts: armada-370: Fix assigned-addresses for every PCIe Root Port
  (pali@kernel.org)
- ARM: dts: dove: Fix assigned-addresses for every PCIe Root Port
  (pali@kernel.org)
- arm64: dts: mt7986: move wed_pcie node (frank-w@public-files.de)
- arm64: tegra: Fix non-prefetchable aperture of PCIe C3 controller
  (vidyas@nvidia.com)
- arm64: tegra: Fix Prefetchable aperture ranges of Tegra234 PCIe controllers
  (vidyas@nvidia.com)
- arm64: dts: mediatek: mt6797: Fix 26M oscillator unit name
  (angelogioacchino.delregno@collabora.com)
- arm64: dts: mediatek: pumpkin-common: Fix devicetree warnings
  (angelogioacchino.delregno@collabora.com)
- arm64: dts: mt2712-evb: Fix usb vbus regulators unit names
  (angelogioacchino.delregno@collabora.com)
- arm64: dts: mt2712-evb: Fix vproc fixed regulators unit names
  (angelogioacchino.delregno@collabora.com)
- arm64: dts: mt2712e: Fix unit address for pinctrl node
  (angelogioacchino.delregno@collabora.com)
- arm64: dts: mt2712e: Fix unit_address_vs_reg warning for oscillators
  (angelogioacchino.delregno@collabora.com)
- arm64: dts: mt6779: Fix devicetree build warnings
  (angelogioacchino.delregno@collabora.com)
- arm64: dts: mt7896a: Fix unit_address_vs_reg warning for oscillator
  (angelogioacchino.delregno@collabora.com)
- arm64: dts: mediatek: mt8195: Fix CPUs capacity-dmips-mhz
  (angelogioacchino.delregno@collabora.com)
- ARM: dts: nuvoton: Remove bogus unit addresses from fixed-partition nodes
  (j.neuschaefer@gmx.net)
- riscv: dts: microchip: remove pcie node from the sev kit
  (conor.dooley@microchip.com)
- arm64: dts: ti: k3-j721s2: Fix the interrupt ranges property for main & wkup
  gpio intr (j-keerthy@ti.com)
- arm64: dts: ti: k3-j7200-mcu-wakeup: Drop dma-coherent in crypto node
  (j-choudhary@ti.com)
- arm64: dts: ti: k3-j721e-main: Drop dma-coherent in crypto node
  (j-choudhary@ti.com)
- arm64: dts: ti: k3-am65-main: Drop dma-coherent in crypto node
  (j-choudhary@ti.com)
- perf/smmuv3: Fix hotplug callback leak in arm_smmu_pmu_init()
  (shangxiaojing@huawei.com)
- perf/arm_dmc620: Fix hotplug callback leak in dmc620_pmu_init()
  (shangxiaojing@huawei.com)
- drivers: perf: marvell_cn10k: Fix hotplug callback leak in tad_pmu_init()
  (yuancan@huawei.com)
- perf: arm_dsu: Fix hotplug callback leak in dsu_pmu_init()
  (yuancan@huawei.com)
- arm64: mm: kfence: only handle translation faults (mark.rutland@arm.com)
- soc: ti: smartreflex: Fix PM disable depth imbalance in omap_sr_probe
  (zhangqilong3@huawei.com)
- soc: ti: knav_qmss_queue: Fix PM disable depth imbalance in knav_queue_probe
  (zhangqilong3@huawei.com)
- riscv: dts: microchip: fix the icicle's #pwm-cells
  (conor.dooley@microchip.com)
- arm: dts: spear600: Fix clcd interrupt (kory.maincent@bootlin.com)
- arm64: dts: qcom: sc7280: Mark all Qualcomm reference boards as LTE
  (quic_sibis@quicinc.com)
- soc/tegra: cbb: Check firewall before enabling error reporting
  (sumitg@nvidia.com)
- soc/tegra: cbb: Add checks for potential out of bound errors
  (sumitg@nvidia.com)
- soc/tegra: cbb: Update slave maps for Tegra234 (sumitg@nvidia.com)
- soc/tegra: cbb: Use correct master_id mask for CBB NOC in Tegra194
  (sumitg@nvidia.com)
- arm64: dts: mt7986: fix trng node name (frank-w@public-files.de)
- soc: sifive: ccache: fix missing of_node_put() in sifive_ccache_init()
  (yangyingliang@huawei.com)
- soc: sifive: ccache: fix missing free_irq() in error path in
  sifive_ccache_init() (yangyingliang@huawei.com)
- soc: sifive: ccache: fix missing iounmap() in error path in
  sifive_ccache_init() (yangyingliang@huawei.com)
- dt-bindings: pwm: fix microchip corePWM's pwm-cells
  (conor.dooley@microchip.com)
- arm64: dts: renesas: r9a09g011: Fix I2C SoC specific strings
  (fabrizio.castro.jz@renesas.com)
- arm64: dts: renesas: r9a09g011: Fix unit address format error
  (fabrizio.castro.jz@renesas.com)
- arm64: dts: renesas: r8a779f0: Fix SCIF "brg_int" clock (wsa+renesas@sang-
  engineering.com)
- arm64: dts: renesas: r8a779f0: Fix HSCIF "brg_int" clock (wsa+renesas@sang-
  engineering.com)
- arm64: dts: qcom: sm6125: fix SDHCI CQE reg names
  (krzysztof.kozlowski@linaro.org)
- arm64: dts: qcom: pm6350: Include header for KEY_POWER
  (marijn.suijten@somainline.org)
- soc: qcom: apr: Add check for idr_alloc and of_property_read_string_index
  (jiasheng@iscas.ac.cn)
- arm64: dts: qcom: sm6350: drop bogus DP PHY clock (johan+linaro@kernel.org)
- arm64: dts: qcom: sm8250: drop bogus DP PHY clock (johan+linaro@kernel.org)
- arm64: dts: qcom: sc7280: fix codec reset line polarity for CRD 1.0/2.0
  (dmitry.torokhov@gmail.com)
- arm64: dts: qcom: sc7280: fix codec reset line polarity for CRD 3.0/3.1
  (dmitry.torokhov@gmail.com)
- arm64: dts: qcom: sm8250-mtp: fix reset line polarity
  (dmitry.torokhov@gmail.com)
- arm64: dts: qcom: msm8996: fix sound card reset line polarity
  (dmitry.torokhov@gmail.com)
- arm64: dts: qcom: sm8450: fix UFS PHY registers (johan+linaro@kernel.org)
- arm64: dts: qcom: sm8350: fix UFS PHY registers (johan+linaro@kernel.org)
- arm64: dts: qcom: sm8250: fix UFS PHY registers (johan+linaro@kernel.org)
- arm64: dts: qcom: sm8150: fix UFS PHY registers (johan+linaro@kernel.org)
- soc: qcom: llcc: make irq truly optional (luca.weiss@fairphone.com)
- arm64: dts: qcom: sc7180-trogdor-homestar: fully configure secondary I2S pins
  (krzysztof.kozlowski@linaro.org)
- arm64: dts: qcom: sm8250: correct LPASS pin pull down
  (krzysztof.kozlowski@linaro.org)
- arm64: dts: qcom: pm660: Use unique ADC5_VCOIN address in node name
  (marijn.suijten@somainline.org)
- riscv: dts: microchip: fix memory node unit address for icicle
  (conor.dooley@microchip.com)
- firmware: ti_sci: Fix polled mode during system suspend (g-vlaev@ti.com)
- drivers: soc: ti: knav_qmss_queue: Mark knav_acc_firmwares as static
  (chenjiahao16@huawei.com)
- ARM: dts: stm32: Fix AV96 WLAN regulator gpio property (marex@denx.de)
- ARM: dts: stm32: Drop stm32mp15xc.dtsi from Avenger96 (marex@denx.de)
- objtool, kcsan: Add volatile read/write instrumentation to whitelist
  (elver@google.com)
- memory: renesas-rpc-if: Clear HS bit during hardware initialization
  (cong.dang.xn@renesas.com)
- arm64: dts: fsd: fix drive strength values as per FSD HW UM
  (p.rajanbabu@samsung.com)
- arm64: dts: fsd: fix drive strength macros as per FSD HW UM
  (p.rajanbabu@samsung.com)
- arm64: dts: qcom: msm8916: Drop MSS fallback compatible
  (stephan.gerhold@kernkonzept.com)
- arm64: dts: qcom: sdm845-cheza: fix AP suspend pin bias
  (krzysztof.kozlowski@linaro.org)
- arm64: dts: qcom: sdm630: fix UART1 pin bias (krzysztof.kozlowski@linaro.org)
- ARM: dts: qcom: apq8064: fix coresight compatible (luca@z3ntu.xyz)
- arm64: dts: qcom: msm8996: fix GPU OPP table (dmitry.baryshkov@linaro.org)
- arm64: dts: qcom: msm8996: fix supported-hw in cpufreq OPP tables
  (dmitry.baryshkov@linaro.org)
- arm64: dts: qcom: msm8996: Add MSM8996 Pro support (y.oudjana@protonmail.com)
- arm64: dts: qcom: sdm845-xiaomi-polaris: fix codec pin conf name
  (krzysztof.kozlowski@linaro.org)
- arm64: dts: qcom: sm8250-sony-xperia-edo: fix touchscreen bias-disable
  (krzysztof.kozlowski@linaro.org)
- arm64: dts: qcom: ipq6018-cp01-c1: use BLSPI1 pins
  (krzysztof.kozlowski@linaro.org)
- arm64: dts: renesas: r8a779g0: Fix HSCIF0 "brg_int" clock
  (geert+renesas@glider.be)
- usb: musb: remove extra check in musb_gadget_vbus_draw
  (ivo.g.dimitrov.75@gmail.com)
- MIPS: DTS: CI20: fix reset line polarity of the ethernet controller
  (dmitry.torokhov@gmail.com)

* Fri Dec 30 2022 Dakkshesh <dakkshesh5@gmail.com> 6.1.1-1
- dejavu: Stable release (6.1.1-1) (dakkshesh5@gmail.com)
- ext4: fix reserved cluster accounting in __es_remove_extent()
  (yebin10@huawei.com)
- ext4: fix inode leak in ext4_xattr_inode_create() on an error path
  (yebin10@huawei.com)
- ext4: allocate extended attribute value in vmalloc area (yebin10@huawei.com)
- ext4: avoid unaccounted block allocation when expanding inode (jack@suse.cz)
- ext4: initialize quota before expanding inode in setproject ioctl
  (jack@suse.cz)
- ext4: stop providing .writepage hook (jack@suse.cz)
- mm: export buffer_migrate_folio_norefs() (jack@suse.cz)
- ext4: switch to using write_cache_pages() for data=journal writeout
  (jack@suse.cz)
- jbd2: switch jbd2_submit_inode_data() to use fs-provided hook for data
  writeout (jack@suse.cz)
- ext4: switch to using ext4_do_writepages() for ordered data writeout
  (jack@suse.cz)
- ext4: move percpu_rwsem protection into ext4_writepages() (jack@suse.cz)
- ext4: provide ext4_do_writepages() (jack@suse.cz)
- ext4: add support for writepages calls that cannot map blocks (jack@suse.cz)
- ext4: drop pointless IO submission from ext4_bio_write_page() (jack@suse.cz)
- ext4: remove nr_submitted from ext4_bio_write_page() (jack@suse.cz)
- ext4: move keep_towrite handling to ext4_bio_write_page() (jack@suse.cz)
- ext4: handle redirtying in ext4_bio_write_page() (jack@suse.cz)
- ext4: fix kernel BUG in 'ext4_write_inline_data_end()' (yebin10@huawei.com)
- ext4: make ext4_mb_initialize_context return void (guoqing.jiang@linux.dev)
- ext4: fix deadlock due to mbcache entry corruption (jack@suse.cz)
- ext4: avoid BUG_ON when creating xattrs (jack@suse.cz)
- fs: ext4: initialize fsdata in pagecache_write() (glider@google.com)
- ext4: fix delayed allocation bug in ext4_clu_mapped for bigalloc + inline
  (enwlinux@gmail.com)
- ext4: fix uninititialized value in 'ext4_evict_inode' (yebin10@huawei.com)
- ext4: fix corruption when online resizing a 1K bigalloc fs
  (libaokun1@huawei.com)
- ext4: fix corrupt backup group descriptors after online resize
  (libaokun1@huawei.com)
- ext4: fix bad checksum after online resize (libaokun1@huawei.com)
- ext4: don't fail GETFSUUID when the caller provides a long buffer
  (djwong@kernel.org)
- ext4: dont return EINVAL from GETFSUUID when reporting UUID length
  (djwong@kernel.org)
- ext4: fix error code return to user-space in ext4_get_branch()
  (lhenriques@suse.de)
- ext4: replace kmem_cache_create with KMEM_CACHE (sunjunchao2870@gmail.com)
- ext4: correct inconsistent error msg in nojournal mode (libaokun1@huawei.com)
- ext4: print file system UUID on mount, remount and unmount
  (lczerner@redhat.com)
- ext4: init quota for 'old.inode' in 'ext4_rename' (yebin10@huawei.com)
- ext4: simplify fast-commit CRC calculation (ebiggers@google.com)
- ext4: fix off-by-one errors in fast-commit block filling
  (ebiggers@google.com)
- ext4: fix unaligned memory access in ext4_fc_reserve_space()
  (ebiggers@google.com)
- ext4: add missing validation of fast-commit record lengths
  (ebiggers@google.com)
- ext4: fix leaking uninitialized memory in fast-commit journal
  (ebiggers@google.com)
- ext4: don't set up encryption key during jbd2 transaction
  (ebiggers@google.com)
- ext4: disable fast-commit of encrypted dir operations (ebiggers@google.com)
- ext4: fix use-after-free in ext4_orphan_cleanup (libaokun1@huawei.com)
- ext4: don't allow journal inode to have encrypt flag (ebiggers@google.com)
- ext4: fix undefined behavior in bit shift for ext4_check_flag_values
  (cuigaosheng1@huawei.com)
- ext4: fix bug_on in __es_tree_search caused by bad boot loader inode
  (libaokun1@huawei.com)
- ext4: add EXT4_IGET_BAD flag to prevent unexpected bad inode
  (libaokun1@huawei.com)
- ext4: add helper to check quota inums (libaokun1@huawei.com)
- ext4: fix bug_on in __es_tree_search caused by bad quota inode
  (libaokun1@huawei.com)
- ext4: remove trailing newline from ext4_msg() message (lhenriques@suse.de)
- jbd2: use the correct print format (cuibixuan@linux.alibaba.com)
- ext4: split ext4_journal_start trace for debug (changfengnan@bytedance.com)
- ext4: journal_path mount options should follow links (lczerner@redhat.com)
- ext4: check the return value of ext4_xattr_inode_dec_ref()
  (floridsleeves@gmail.com)
- ext4: remove redundant variable err (cui.jinpeng2@zte.com.cn)
- ext4: add inode table check in __ext4_get_inode_loc to aovid possible
  infinite loop (libaokun1@huawei.com)
- fs/ext4: replace ternary operator with min()/max() and min_t()
  (yijiangshan@kylinos.cn)
- ext4: check and assert if marking an no_delete evicting inode dirty
  (yi.zhang@huawei.com)
- ext4: silence the warning when evicting inode with dioread_nolock
  (yi.zhang@huawei.com)
- fsverity: simplify fsverity_get_digest() (ebiggers@google.com)
- fsverity: stop using PG_error to track error status (ebiggers@google.com)
- fscrypt: add additional documentation for SM4 support (ebiggers@google.com)
- fscrypt: remove unused Speck definitions (ebiggers@google.com)
- fscrypt: Add SM4 XTS/CTS symmetric algorithm support
  (tianjia.zhang@linux.alibaba.com)
- blk-crypto: Add support for SM4-XTS blk crypto mode
  (tianjia.zhang@linux.alibaba.com)
- fscrypt: add comment for fscrypt_valid_enc_modes_v1() (ebiggers@google.com)
- fscrypt: pass super_block to fscrypt_put_master_key_activeref()
  (ebiggers@google.com)
- f2fs: reset wait_ms to default if any of the victims have been selected
  (ssawgyw@gmail.com)
- f2fs: fix some format WARNING in debug.c and sysfs.c (frank.li@vivo.com)
- f2fs: don't call f2fs_issue_discard_timeout() when discard_cmd_cnt is 0 in
  f2fs_put_super() (frank.li@vivo.com)
- f2fs: fix iostat parameter for discard (frank.li@vivo.com)
- f2fs: Fix spelling mistake in label: free_bio_enrty_cache ->
  free_bio_entry_cache (colin.i.king@gmail.com)
- f2fs: add block_age-based extent cache (jaegeuk@kernel.org)
- f2fs: allocate the extent_cache by default (jaegeuk@kernel.org)
- f2fs: refactor extent_cache to support for read and more (jaegeuk@kernel.org)
- f2fs: remove unnecessary __init_extent_tree (jaegeuk@kernel.org)
- f2fs: move internal functions into extent_cache.c (jaegeuk@kernel.org)
- f2fs: specify extent cache for read explicitly (jaegeuk@kernel.org)
- f2fs: introduce f2fs_is_readonly() for readability (frank.li@vivo.com)
- f2fs: remove F2FS_SET_FEATURE() and F2FS_CLEAR_FEATURE() macro
  (frank.li@vivo.com)
- f2fs: do some cleanup for f2fs module init (frank.li@vivo.com)
- MAINTAINERS: Add f2fs bug tracker link (chao@kernel.org)
- f2fs: remove the unused flush argument to change_curseg (hch@lst.de)
- f2fs: open code allocate_segment_by_default (hch@lst.de)
- f2fs: remove struct segment_allocation default_salloc_ops (hch@lst.de)
- f2fs: introduce discard_urgent_util sysfs node (frank.li@vivo.com)
- f2fs: define MIN_DISCARD_GRANULARITY macro (frank.li@vivo.com)
- f2fs: init discard policy after thread wakeup (frank.li@vivo.com)
- f2fs: avoid victim selection from previous victim section
  (yonggil.song@samsung.com)
- f2fs: truncate blocks in batch in __complete_revoke_list() (chao@kernel.org)
- f2fs: make __queue_discard_cmd() return void (frank.li@vivo.com)
- f2fs: fix description about discard_granularity node (frank.li@vivo.com)
- f2fs: move set_file_temperature into f2fs_new_inode (shengyong@oppo.com)
- f2fs: fix to enable compress for newly created file if extension matches
  (shengyong@oppo.com)
- f2fs: set zstd compress level correctly (shengyong@oppo.com)
- f2fs: change type for 'sbi->readdir_ra' (ssawgyw@gmail.com)
- f2fs: cleanup for 'f2fs_tuning_parameters' function (ssawgyw@gmail.com)
- f2fs: fix to alloc_mode changed after remount on a small volume device
  (ssawgyw@gmail.com)
- f2fs: remove submit label in __submit_discard_cmd() (frank.li@vivo.com)
- f2fs: fix to do sanity check on i_extra_isize in is_alive() (chao@kernel.org)
- f2fs: introduce F2FS_IOC_START_ATOMIC_REPLACE (daehojeong@google.com)
- f2fs: fix to set flush_merge opt and show noflush_merge (frank.li@vivo.com)
- f2fs: initialize locks earlier in f2fs_fill_super() (penguin-
  kernel@I-love.SAKURA.ne.jp)
- f2fs: optimize iteration over sparse directories (chao@kernel.org)
- f2fs: fix to avoid accessing uninitialized spinlock (chao@kernel.org)
- f2fs: correct i_size change for atomic writes (daehojeong@google.com)
- f2fs: add proc entry to show discard_plist info (frank.li@vivo.com)
- f2fs: allow to read node block after shutdown (jaegeuk@kernel.org)
- f2fs: replace ternary operator with max() (wangkailong@jari.cn)
- f2fs: replace gc_urgent_high_remaining with gc_remaining_trials
  (frank.li@vivo.com)
- f2fs: add missing bracket in doc (jaegeuk@kernel.org)
- f2fs: use sysfs_emit instead of sprintf (jaegeuk@kernel.org)
- f2fs: introduce gc_mode sysfs node (frank.li@vivo.com)
- f2fs: fix to destroy sbi->post_read_wq in error path of f2fs_fill_super()
  (chao@kernel.org)
- f2fs: fix return val in f2fs_start_ckpt_thread() (frank.li@vivo.com)
- f2fs: fix the msg data type (quic_mojha@quicinc.com)
- f2fs: fix the assign logic of iocb (quic_mojha@quicinc.com)
- f2fs: Fix typo in comments (keosung.park@samsung.com)
- f2fs: introduce max_ordered_discard sysfs node (frank.li@vivo.com)
- f2fs: allow to set compression for inlined file (jaegeuk@kernel.org)
- f2fs: add barrier mount option (frank.li@vivo.com)
- f2fs: fix normal discard process (zhangdongdong1@oppo.com)
- f2fs: cleanup in f2fs_create_flush_cmd_control() (frank.li@vivo.com)
- f2fs: fix gc mode when gc_urgent_high_remaining is 1 (frank.li@vivo.com)
- f2fs: remove batched_trim_sections node (frank.li@vivo.com)
- f2fs: support fault injection for f2fs_is_valid_blkaddr() (chao@kernel.org)
- f2fs: fix to invalidate dcc->f2fs_issue_discard in error path
  (chao@kernel.org)
- f2fs: Fix the race condition of resize flag between resizefs
  (zhangqilong3@huawei.com)
- f2fs: let's avoid to get cp_rwsem twice by f2fs_evict_inode by d_invalidate
  (jaegeuk@kernel.org)
- f2fs: should put a page when checking the summary info (pavel@denx.de)

* Fri Dec 30 2022 Dakkshesh <dakkshesh5@gmail.com> 6.1.1-rc3
- dejavu: rc3 (dakkshesh5@gmail.com)
- buildtar: fix tarballs with EFI_ZBOOT enabled (vkabatov@redhat.com)
- modpost: Include '.text.*' in TEXT_SECTIONS (nathan@kernel.org)
- padata: Mark padata_work_init() as __ref (nathan@kernel.org)
- kbuild: ensure Make >= 3.82 is used (masahiroy@kernel.org)
- kbuild: refactor the prerequisites of the modpost rule (masahiroy@kernel.org)
- kbuild: change module.order to list *.o instead of *.ko
  (masahiroy@kernel.org)
- kbuild: use .NOTINTERMEDIATE for future GNU Make versions
  (masahiroy@kernel.org)
- kconfig: refactor Makefile to reduce process forks (masahiroy@kernel.org)
- kbuild: add read-file macro (masahiroy@kernel.org)
- kbuild: do not sort after reading modules.order (masahiroy@kernel.org)
- kbuild: add test-{ge,gt,le,lt} macros (masahiroy@kernel.org)
- Documentation: raise minimum supported version of binutils to 2.25
  (masahiroy@kernel.org)
- kbuild: add -Wundef to KBUILD_CPPFLAGS for W=1 builds (masahiroy@kernel.org)
- kbuild: move -Werror from KBUILD_CFLAGS to KBUILD_CPPFLAGS
  (masahiroy@kernel.org)
- kbuild: Port silent mode detection to future gnu make.
  (dgoncharov@users.sf.net)
- init/version.c: remove #include <generated/utsrelease.h>
  (linux@weissschuh.net)
- firmware_loader: remove #include <generated/utsrelease.h>
  (linux@weissschuh.net)
- modpost: Mark uuid_le type to be suitable only for MEI
  (andriy.shevchenko@linux.intel.com)
- kbuild: add ability to make source rpm buildable using koji
  (ivecera@redhat.com)
- kbuild: warn objects shared among multiple modules (masahiroy@kernel.org)
- kbuild: add kbuild-file macro (masahiroy@kernel.org)
- kbuild: deb-pkg: get rid of |flex:native workaround from Build-Depends
  (masahiroy@kernel.org)
- scripts/jobserver-exec: parse the last --jobserver-auth= option
  (masahiroy@kernel.org)
- kconfig: remove redundant (void *) cast in search_conf()
  (masahiroy@kernel.org)
- kconfig: remove const qualifier from str_get() (masahiroy@kernel.org)
- kconfig: remove unneeded variable in get_prompt_str() (masahiroy@kernel.org)
- modpost: fix array_size.cocci warning (wangkailong@jari.cn)
- Makefile.debug: support for -gz=zstd (ndesaulniers@google.com)
- modpost: Join broken long printed messages (geert+renesas@glider.be)
- pstore: Properly assign mem_type property (luca@osomprivacy.com)
- pstore: Make sure CONFIG_PSTORE_PMSG selects CONFIG_RT_MUTEXES
  (jstultz@google.com)
- pstore: Switch pmsg_lock to an rt_mutex to avoid priority inversion
  (jstultz@google.com)
- pstore: Avoid kcore oops by vmap()ing with VM_IOREMAP (swboyd@chromium.org)
- pstore/ram: Fix error return code in ramoops_probe() (wangyufen@huawei.com)
- pstore: Alert on backend write error (gpiccoli@igalia.com)
- MAINTAINERS: Update pstore maintainers (keescook@chromium.org)
- pstore/ram: Set freed addresses to NULL (keescook@chromium.org)
- pstore/ram: Move internal definitions out of kernel-wide include
  (keescook@chromium.org)
- pstore/ram: Move pmsg init earlier (keescook@chromium.org)
- pstore/ram: Consolidate kfree() paths (keescook@chromium.org)
- efi: pstore: Follow convention for the efi-pstore backend name
  (gpiccoli@igalia.com)
- pstore: Inform unregistered backend names as well (gpiccoli@igalia.com)
- pstore: Expose kmsg_bytes as a module parameter (gpiccoli@igalia.com)
- pstore: Improve error reporting in case of backend overlap
  (gpiccoli@igalia.com)
- pstore/zone: Use GFP_ATOMIC to allocate zone buffer (hqjagain@gmail.com)
- x86/configs: fedora: Make XFS driver built-in (dakkshesh5@gmail.com)

* Fri Dec 30 2022 Dakkshesh <dakkshesh5@gmail.com> 6.1.1-2
- fs/remap_range: avoid spurious writeback on zero length request
  (bfoster@redhat.com)
- xfs: remove restrictions for fsdax and reflink (ruansy.fnst@fujitsu.com)
- fsdax,xfs: port unshare to fsdax (ruansy.fnst@fujitsu.com)
- xfs: use dax ops for zero and truncate in fsdax mode
  (ruansy.fnst@fujitsu.com)
- fsdax: dedupe: iter two files at the same time (ruansy.fnst@fujitsu.com)
- fsdax,xfs: set the shared flag when file extent is shared
  (ruansy.fnst@fujitsu.com)
- fsdax: zero the edges if source is HOLE or UNWRITTEN
  (ruansy.fnst@fujitsu.com)
- fsdax: invalidate pages when CoW (ruansy.fnst@fujitsu.com)
- fsdax: introduce page->share for fsdax in reflink mode
  (ruansy.fnst@fujitsu.com)
- xfs: dquot shrinker doesn't check for XFS_DQFLAG_FREEING
  (dchinner@redhat.com)
- xfs: Remove duplicated include in xfs_iomap.c (yang.lee@linux.alibaba.com)
- xfs: invalidate xfs_bufs when allocating cow extents (djwong@kernel.org)
- xfs: get rid of assert from xfs_btree_islastblock (guoxuenan@huawei.com)
- xfs: estimate post-merge refcounts correctly (djwong@kernel.org)
- xfs: hoist refcount record merge predicates (djwong@kernel.org)
- xfs: wait iclog complete before tearing down AIL (guoxuenan@huawei.com)
- xfs: attach dquots to inode before reading data/cow fork mappings
  (djwong@kernel.org)
- xfs: shut up -Wuninitialized in xfsaild_push (djwong@kernel.org)
- xfs: use memcpy, not strncpy, to format the attr prefix during listxattr
  (djwong@kernel.org)
- xfs: invalidate block device page cache during unmount (djwong@kernel.org)
- xfs: add debug knob to slow down write for fun (djwong@kernel.org)
- xfs: add debug knob to slow down writeback for fun (djwong@kernel.org)
- xfs: drop write error injection is unfixable, remove it (dchinner@redhat.com)
- xfs: use iomap_valid method to detect stale cached iomaps
  (dchinner@redhat.com)
- iomap: write iomap validity checks (dchinner@redhat.com)
- xfs: xfs_bmap_punch_delalloc_range() should take a byte range
  (dchinner@redhat.com)
- iomap: buffered write failure should not truncate the page cache
  (dchinner@redhat.com)
- xfs,iomap: move delalloc punching to iomap (dchinner@redhat.com)
- xfs: use byte ranges for write cleanup ranges (dchinner@redhat.com)
- xfs: punching delalloc extents on write failure is racy (dchinner@redhat.com)
- xfs: fix incorrect error-out in xfs_remove (djwong@kernel.org)
- xfs: check inode core when scrubbing metadata files (djwong@kernel.org)
- xfs: don't warn about files that are exactly s_maxbytes long
  (djwong@kernel.org)
- xfs: teach scrub to flag non-extents format cow forks (djwong@kernel.org)
- xfs: check that CoW fork extents are not shared (djwong@kernel.org)
- xfs: check quota files for unwritten extents (djwong@kernel.org)
- xfs: block map scrub should handle incore delalloc reservations
  (djwong@kernel.org)
- xfs: teach scrub to check for adjacent bmaps when rmap larger than bmap
  (djwong@kernel.org)
- xfs: fix perag loop in xchk_bmap_check_rmaps (djwong@kernel.org)
- xfs: online checking of the free rt extent count (djwong@kernel.org)
- xfs: skip fscounters comparisons when the scan is incomplete
  (djwong@kernel.org)
- xfs: make rtbitmap ILOCKing consistent when scanning the rt bitmap file
  (djwong@kernel.org)
- xfs: load rtbitmap and rtsummary extent mapping btrees at mount time
  (djwong@kernel.org)
- xfs: don't return -EFSCORRUPTED from repair when resources cannot be grabbed
  (djwong@kernel.org)
- xfs: don't retry repairs harder when EAGAIN is returned (djwong@kernel.org)
- xfs: fix return code when fatal signal encountered during dquot scrub
  (djwong@kernel.org)
- xfs: return EINTR when a fatal signal terminates scrub (djwong@kernel.org)
- xfs: pivot online scrub away from kmem.[ch] (djwong@kernel.org)
- xfs: initialize the check_owner object fully (djwong@kernel.org)
- xfs: standardize GFP flags usage in online scrub (djwong@kernel.org)
- xfs: make AGFL repair function avoid crosslinked blocks (djwong@kernel.org)
- xfs: log the AGI/AGF buffers when rolling transactions during an AG repair
  (djwong@kernel.org)
- xfs: don't track the AGFL buffer in the scrub AG context (djwong@kernel.org)
- xfs: fully initialize xfs_da_args in xchk_directory_blocks
  (djwong@kernel.org)
- xfs: write page faults in iomap are not buffered writes (dchinner@redhat.com)
- scatterlist: Don't allocate sg lists using __get_free_page
  (sultan@kerneltoast.com)
- mm: Disable proactive compaction by default (sultan@kerneltoast.com)
- mm: Don't hog the CPU and zone lock in rmqueue_bulk()
  (sultan@kerneltoast.com)
- mm: Lower the non-hugetlbpage pageblock size to reduce scheduling delays
  (sultan@kerneltoast.com)
- mm: Stop kswapd early when nothing's waiting for it to free pages
  (sultan@kerneltoast.com)
- mm: Disable watermark boosting by default (sultan@kerneltoast.com)
- Bump release ver to v6.1.1-2
* Thu Dec 29 2022 Dakkshesh <dakkshesh5@gmail.com> 6.1.1-1
- Initial release (v6.1.1-1)

