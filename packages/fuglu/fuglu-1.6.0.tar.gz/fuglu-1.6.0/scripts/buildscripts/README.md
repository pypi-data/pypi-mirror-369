# how to build fuglu in deb package
1. start a container to build the deb package. Note on the volume path mapping
```
$ docker run --rm --name fuglu_doc -it -v /fuglu/:/fuglu debian:12
```

2. build fuglu deb package
```
# cd fuglu/fuglu
# bash ./scripts/build/build-deb.sh
```

3. build debian package should be available in `fuglu/deb_dist` directory

