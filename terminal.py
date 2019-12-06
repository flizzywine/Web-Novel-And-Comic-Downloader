import argparse
import downloader

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("urls")
    parser.add_argument("end_url")
    parser.add_argument("--out_filename","-o")
    parser.add_argument("--title","-t")
    parser.add_argument("--body","-b")
    
    args = parser.parse_args()
    urls, out, title, body = args.urls, args.out_filename, \
        args.title, args.body
    
    downloader.parse(urls, title, body, out)
    
    downloader.download()
