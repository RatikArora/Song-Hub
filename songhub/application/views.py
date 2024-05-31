import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import Search
from pytube import YouTube
from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
import os
import zipfile

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id='c66fdec5ec1f48389bc463a67a62ee3e', client_secret='56467565c46942bb85dfd14082f6e2cb'))

url = 1
# Create your views here.
def main(request):
    if request.method=="POST":
        global url 
        url = request.POST.get('url')
        try :
            results = sp.playlist_tracks(url)
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 404:
                # Redirect to the main page with an error message
                return redirect('main')  # Replace 'main_page' with the correct URL name for your main page
            else:
                return HttpResponse("An error occurred: " + str(e))
            
        # print(url)
        return render(request,'loading.html')
    return render(request,'first.html')



def loading(request):
    return render(request,'loading.html')


def loading2(request):
    donwloader(url)
    i = read_i_from_file()
    # print(i,type(i))
    content = {
        'i':i
               }
    return render(request, 'loading2.html', content)

def read_i_from_file():
    with open('application/value_of_i.txt', 'r') as f:
        i = int(f.read())
    return i

def update_i_in_file(i):
    with open('application/value_of_i.txt', 'w') as f:
        f.write(str(i))

def get_upload_folder_name(i):
    return os.path.join('uploads', str(i))

def create_upload_directory():
    i = read_i_from_file()  # Read the current value of i
    i += 1  # Increment i
    update_i_in_file(i)  # Update i in the file

    # Generate folder name based on 'i' and create the folder
    folder_path = os.path.join(settings.MEDIA_ROOT, get_upload_folder_name(i))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return i  # Return the new value of i



def donwloader(url):
    try: 
        i = create_upload_directory()
        results = sp.playlist_tracks(url)
        # print(results)
        tracks = results['items']

        for index, track in enumerate(tracks):
            song_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']
            query = f"{song_name} {artist_name}"
            search_results = Search(query).results

            if search_results:
                video = search_results[0]
                video_url = f'https://www.youtube.com/watch?v={video.video_id}'
                # print(video_url)
                yt = YouTube(video_url)
                audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
                
                
                file_path = os.path.join(settings.MEDIA_ROOT, get_upload_folder_name(i))
                audio_stream.download(output_path=file_path)

                print(f"Track Name: {track['track']['name']}, Artist: {track['track']['artists'][0]['name']}")

        def zip_mp4_files(folder_path, output_path):
            # Ensure the output file has a .zip extension
            if not output_path.endswith('.zip'):
                output_path += '.zip'

            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        if file.lower().endswith('.mp4'):
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, folder_path)
                            zipf.write(file_path, arcname=arcname)

        # Example usage:
        folder_path = f'media/uploads/{i}'  # Replace with the folder path you want to zip
        output_path = f'media/uploads/{i}/{i}.zip'  # Replace with the desired output zip file path

        zip_mp4_files(folder_path, output_path)
    except:
        return HttpResponse("An error occurred: At our end sorry !")

# to serve the file to the user
def download(request, i):
    zip_file_path = os.path.join(settings.MEDIA_ROOT, f'uploads/{i}/{i}.zip')

    with open(zip_file_path, 'rb') as zip_file:
        response = HttpResponse(zip_file.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{i}.zip"'
        return response
    
