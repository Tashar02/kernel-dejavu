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
%define _stablekver 2
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

