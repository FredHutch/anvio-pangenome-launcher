# Anvi'o Pangenome Launcher
Small application to launch the anvi'o pangenome browser

The purpose of this tool is to simply launch the amazing 
[anvi'o](http://merenlab.org/software/anvio/) tool inside a
Docker container, loading up a set of pan-genome results in
a browser window for the user to interact with.

Anvi'o does many things -- at the moment this launcher only
supports analyses which have been created with the pan-genome
analysis modules. Specifically, the workflow for running anvi'o
which be found at [github.com/FredHutch/nf-anvio-pangenome](https://github.com/FredHutch/nf-anvio-pangenome). This workflow creates two `"*.db"` files,
one named `"*-GENOMES.db"` and one named `"*-PAN.db"`. As
long as those two files are present in the same folder, then
this launcher will be able to render them in a browser window.


### Prerequisites

1. Install Docker

Depending on your system, there are a few different ways to
install Docker. Take a look at 
[the installation instructions](https://docs.docker.com/install/)
and pick whichever applies to you. After Docker has been installed,
you may need to get it started as an additional step.


2. Get the launcher

The launcher has been compiled as an executable for three different
platforms, Windows, Ubuntu, and macOS. Visit the
[release page](https://github.com/FredHutch/anvio-pangenome-launcher/releases)
and pick the `launch_anvio` file which is appropriate for you.


### Running the launcher

Once you have downloaded the launcher, move it to somewhere where
you can find it, such as an application folder. When you try to
run it the first time, you may also have to confirm with your
operating system that the executable is trustworthy -- this process
is a bit different for each operating system but it shouldn't be
too complicated in the end.

1. Start the launcher (double click, etc.)
2. Pick the input files -- select either the `"*-GENOMES.db"` or `"*-PAN.db"` file
3. Wait for anvi'o to load. If the Docker image hasn't been downloaded, this may take some time. Once the Docker image is downloaded, it will take ~1 min for anvi'o to get started. Once it has loaded, a browser window will automatically open. Sometimes you also have to refresh the page in order for it to render nicely.
4. Get going with anvi'o! [There's a lot to explore in the pangenome tool.](http://merenlab.org/2016/11/08/pangenomics-v2/)


### Disclaimer

This launcher has only been tested on macOS -- please report any
problems or issues to the authors for help and troubleshooting.
Also feel free to 
[report an issue](https://github.com/FredHutch/anvio-pangenome-launcher/issues)
for additional help.


### Maintainer

Samuel Minot - first initial and last name at fred hutch dot org.
