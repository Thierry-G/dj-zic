import logging

def setup_logging(log_file='/opt/djZic/log/dj_music.log', enable_logging=True):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    if enable_logging and not logger.handlers:
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        logger.addHandler(fh)
    
    return logger
