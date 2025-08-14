from oslo_config import cfg


def parse_args(args, **kwargs):
    cfg.CONF(args,
             project='certx',
             **kwargs)
