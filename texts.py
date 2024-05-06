from global_static_vars import line_args

def tr(a,b):
    country = line_args['country']
    if country == 'SK' or country == 'sk':
        return b
    else:
        return a

clickToContinue = lambda: tr("Click to continue","Kliknite pre pokračovanie")
rating_scale_text = lambda: tr("(1 - not liked, 7 - liked a lot)", "(1 - vôbec sa mi nepáči, 7 - veľmi sa mi páči)")