import os
import re
from base import *

class x264(Base):
    def __init__(self):
        self.name = "x264"
        self.version = "e61d9f9d3d77584136a591e01cebecbd7547a43b"
        self.compilers = [Base.COMPILER_MAC_GCC,Base.COMPILER_MAC_CLANG,Base.COMPILER_WIN_MSVC2010] # Base.COMPILER_WIN_MSVC2010, Base.COMPILER_WIN_MSVC2012, 
        self.arch = [Base.ARCH_M32, Base.ARCH_M64]
        self.dependencies = ["yasm"]
        self.info = "Windows build needs mingw"

    def download(self): 
        rb_git_clone(self, "git://git.videolan.org/x264.git", self.version)

    def build(self):

        dbg_flag = " --enable-debug --disable-asm " if rb_is_debug() else ""

        if rb_is_unix():

            host = ""
            if rb_is_32bit():
                host = " --host=$(./config.guess | sed \"s/x86_64/i386/g\")"

            dd = rb_get_download_dir(self)
            env_vars = rb_get_autotools_environment_vars()
            cmd = [
                "set -x",
                "cd " +dd,
                "./configure " +rb_get_configure_prefix_flag() +dbg_flag +" --enable-static " +host,
                "make clean",
                "make install"
                ]

            opts = " --enable-static " +dbg_flag 
            rb_execute_shell_commands(self, cmd, env_vars);
            #rb_build_with_autotools(self, opts)
        elif rb_is_msvc():
            # because we're using msvc we cannot trust the import library from 
            # mingw, therefore we use the LIB tool to create our own.
            dd = rb_get_download_dir(self)
            version = re.search("#define X264_BUILD ([0-9]*)", open(dd +"x264.h").read())
            version = version.group(1)

            #"version=$(grep -i \"#define X264_BUILD \" x264.h | sed 's/#define X264_BUILD //g')",
            cmd = (
                "cd " +rb_mingw_windows_path_to_cygwin_path(dd),
      
                "./configure " +rb_mingw_get_configure_prefix_flag() +" --cross-prefix=i686-w64-mingw32- --host=i686-w64-mingw32 --disable-cli --enable-shared " +dbg_flag +" --enable-win32thread --extra-ldflags=\"-Wl,--output-def=libx264.def\"",
                "sed \"s/HANDLE hinstDLL/HINSTANCE hinstDLL/g\" x264dll.c > x264dll.c.new",
                "mv x264dll.c x264dll.orig",
                "mv x264dll.c.new x264dll.c",
                "make clean",
                "make",
                "mv libx264.def libx264-" +version +".def",
                "make install"
            )
            rb_mingw_execute_shell_commands(self, cmd)

            cmd = (
                "cd " +dd,
                "LIB.exe /DEF:libx264-" +version +".def"
                )
            rb_execute_shell_commands(self, cmd)
            


    def is_build(self):
        if rb_is_unix():
            return rb_install_lib_file_exists("libx264.a")
        elif rb_is_win():
            return rb_deploy_lib_file_exists("libx264-138.lib")
        else:
            rb_red_ln("Cannot check if the lib is build on this platform")
    
    def deploy(self):
        if rb_is_unix():
            rb_deploy_lib(rb_install_get_lib_file("libx264.a"))
            rb_deploy_header(rb_install_get_include_file("x264.h"))
            rb_deploy_header(rb_install_get_include_file("x264_config.h"))
        elif rb_is_win():
            rb_deploy_lib(rb_download_get_file(self, "libx264-138.lib"))
            rb_deploy_dll(rb_install_get_bin_file("libx264-138.dll"))
            rb_deploy_header(rb_install_get_include_file("x264.h"))
            rb_deploy_header(rb_install_get_include_file("x264_config.h"))
        else:
            rb_red_ln("@todo")

