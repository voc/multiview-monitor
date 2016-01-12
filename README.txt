we need intervideosink/src for jumping the blocking barrier
so src and sink need to run in the same process
because ffmpeg needs to run in a separate process, we need an fdsrc like input pipeline

the thing is, we also manage the input ffmpegs as well
