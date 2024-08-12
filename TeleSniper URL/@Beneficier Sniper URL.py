import time
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UsernameOccupiedError, PhoneNumberBannedError, ChannelPrivateError
from telethon.tl.functions.channels import CreateChannelRequest, UpdateUsernameRequest
from telethon.tl.functions.account import CheckUsernameRequest

API_ID = 'YOUR_API_ID'  
API_HASH = 'YOUR_API_HASH'  
PHONE_NUMBER = 'YOUR_PHONE_NUMBER'  
CHECK_INTERVAL = 15  

client = TelegramClient('telesniper_session', API_ID, API_HASH)

def get_usernames_from_file(file_path):
    with open(file_path, 'r') as file:
        usernames = file.read().splitlines()
    return usernames

async def check_username_availability(username):
    try:
        result = await client(CheckUsernameRequest(username))
        return result
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de la disponibilité du nom d'utilisateur @{username}: {e}")
        return False

async def create_public_channel(username):
    try:
        channel_name = f"{username} Sniper"
        description = f"URL Snipée par @benenficier"
        result = await client(CreateChannelRequest(
            title=channel_name,
            about=description,
            megagroup=False
        ))

        channel_id = result.chats[0].id  
        print(f"✅ Canal public créé : {channel_name} avec la description '{description}'")

        time.sleep(10)  

        try:
            await client(UpdateUsernameRequest(
                channel=channel_id,
                username=username
            ))
            print(f"✅ Nom d'utilisateur mis à jour : @{username}")
            print(f"🌐 URL du canal : https://t.me/{username}")
        except UsernameOccupiedError:
            print(f"❌ Nom d'utilisateur @{username} déjà pris après création du canal.")
        except FloodWaitError as e:
            print(f"⏳ Une attente de {e.seconds} secondes est requise avant de définir le nom d'utilisateur.")
            for remaining in range(e.seconds, 0, -1):
                print(f"⏳ En attente de {remaining} secondes...", end="\r")
                time.sleep(1)
            print("\n⏳ Attente terminée, réessayons de mettre à jour le nom d'utilisateur.")
            await client(UpdateUsernameRequest(
                channel=channel_id,
                username=username
            ))
            print(f"✅ Nom d'utilisateur mis à jour : @{username}")
            print(f"🌐 URL du canal : https://t.me/{username}")
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du nom d'utilisateur : {e}")

    except FloodWaitError as e:
        print(f"⏳ Attente de {e.seconds} secondes en raison d'une erreur de limitation.")
        time.sleep(e.seconds)
    except PhoneNumberBannedError:
        print("❌ Le numéro de téléphone est banni.")
    except ChannelPrivateError:
        print("❌ Le canal est privé. Assurez-vous que le canal est configuré comme public.")
    except Exception as e:
        print(f"❌ Erreur lors de la création du canal : {e}")

async def main():
    await client.start(PHONE_NUMBER)
    
    file_path = input("📂 Entrez le chemin du fichier texte contenant les noms d'utilisateur à vérifier : ")
    usernames = get_usernames_from_file(file_path)
    
    while True:
        for username in usernames:
            if username.isalnum():
                print(f"✅ Nom d'utilisateur valide : {username}")
                
                if await check_username_availability(username):
                    print(f"✅ Nom d'utilisateur disponible : {username}")
                    await create_public_channel(username)
                    break
                else:
                    print(f"❌ Nom d'utilisateur non disponible : {username}")
            else:
                print(f"❌ Nom d'utilisateur non valide : {username}")
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
