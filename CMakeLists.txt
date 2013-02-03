cmake_minimum_required(VERSION 2.8)

include(RezBuild)

file(GLOB_RECURSE bin_files "bin/*")
rez_install_files(
	${bin_files}
    DESTINATION .
    EXECUTABLE
)

file(GLOB_RECURSE py_files "python/*.py")
rez_install_python(
    py
    FILES ${py_files}
    DESTINATION .
)

include(RezInstallDoxygen)
file(GLOB_RECURSE doc_files "docs/*")

rez_install_doxygen(
    doc
    FILES  ${doc_files}
    DESTINATION doc
    

    # remove this once your docs have stabilised, then they will only be built and 
    # installed when you're performing a central install (ie a rez-release).
    FORCE 
)

