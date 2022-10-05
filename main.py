from anime import Anime

sn_tuple = (
    28798,
    28889,
    29006,
    29007,
    29240,
    29241,
    29486,
    29487,
    29605,
    29606,
    29773,
    29774,
    31501
)

for sn in sn_tuple:
    Anime(sn).download()
# Anime(31584).download(resolution= 360)
