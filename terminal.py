import argparse
import downloader

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("start_url")
    parser.add_argument("end_url")
    parser.add_argument("--out_filename","-o")
    parser.add_argument("--title","-t")
    parser.add_argument("--body","-b")
    
    args = parser.parse_args()
    start, end, out, title, body = args.start_url, args.end_url, args.out_filename, \
        args.title, args.body
    
    downloader.parse(start, end, title, body, out)
    
    downloader.download()
