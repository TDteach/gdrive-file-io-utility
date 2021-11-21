import os
import traceback

from drive_io import DriveIO



def selecte_files(file_list):
    if len(file_list) == 0:
        return None

    for k, gfile in enumerate(file_list):
        print(k+1, gfile.name, gfile.parents, gfile.id)

    if len(file_list) == 1:
        return file_list[0]

    selected_gfile = None
    while selected_gfile is None:
        print('input the index number (0 for cancel):')
        idx=int(input())
        print(idx)
        if idx>0 and idx<=len(file_list):
            selected_gfile=file_list[idx-1]
            print('Select file {} with id {}.'.format(selected_gfile.name, selected_gfile.id))
        elif idx == 0:
            print('Exit.')
            break
        else:
            continue
    return selected_gfile



def download_gfile(g_drive, gfile, output_filepath):
    if not os.path.exists(output_filepath):
        os.makedirs(output_filepath)

    print('Downloading ...')
    g_drive.download(gfile, output_filepath)
    print('Downloading over! stored at '+os.path.join(output_filepath, gfile.name))


def download_folder(g_drive, selected_gfile, output_filepath):
    fd_id = selected_gfile.id
    query = "'{}' in parents ".format(fd_id)
    file_list = g_drive.query_worker(query)
    for k, gfile in enumerate(file_list):
        print(k+1, gfile.name, gfile.parents, gfile.id)
        if gfile.mimeType.endswith('folder'):
            download_folder(g_drive, gfile, os.path.join(output_filepath, gfile.name))
        else:
            download_gfile(g_drive, gfile, output_filepath)



def download(token, filename, output_filepath):
    if not os.path.exists(output_filepath):
        os.makedirs(output_filepath)

    print('Instantiating Drive object')
    g_drive = DriveIO(token)

    print('Making query to drive')
    query = "name contains '{}' and trashed = false".format(filename)
    print(query)
    file_list = g_drive.query_worker(query)

    selected_gfile = selecte_files(file_list)
    if selected_gfile is not None:
        mimeType = selected_gfile.mimeType
        if mimeType.endswith('folder'):
            download_folder(g_drive, selected_gfile, os.path.join(output_filepath, selected_gfile.name))
        else:
            download_gfile(g_drive, selected_gfile, output_filepath)



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Upload a folder to the trojai google drive.')

    parser.add_argument('--token-pickle-filepath', type=str,
                        help='Path token.pickle file holding the oauth keys.',
                        default='token.pickle')
    parser.add_argument('--filename', type=str,
                        help='The filename to download from drive',
                        required=True)
    parser.add_argument('--output_dirpath', type=str,
                        help='The folder to download into on your local machine',
                        required=True)

    args = parser.parse_args()

    token = args.token_pickle_filepath
    filename = args.filename
    output_dirpath = args.output_dirpath
    print('Args: ')
    print('token = {}'.format(token))
    print('filename = {}'.format(filename))
    print('output_dirpath = {}'.format(output_dirpath))

    try_nb = 0
    max_nb_tries = 1
    done = False
    while not done and try_nb < max_nb_tries:
        try:
            try_nb = try_nb + 1
            download(token, filename, output_dirpath)
            done = True
        except Exception as e:
            traceback.print_exc()
            traceback.print_stack()
            print('failed, retrying')
            pass



