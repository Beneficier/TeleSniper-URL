import time
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UsernameOccupiedError, PhoneNumberBannedError, ChannelPrivateError
from telethon.tl.functions.channels import CreateChannelRequest, UpdateUsernameRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.channels import GetChannelsRequest

# Configuration
API_ID = '29201382'  # Votre API_ID Telegram
API_HASH = '112aeb6a52c63d73f1787ecc38082b50'  # Votre API_HASH Telegram
PHONE_NUMBER = '+62 819 39031356'  # Votre numéro de téléphone Telegram
CHECK_INTERVAL = 15  # Intervalle de vérification en secondes

# Connexion au client Telegram
client = TelegramClient('telesniper_session', API_ID, API_HASH)

def get_usernames_from_file(file_path):
    """Lit les noms d'utilisateur depuis le fichier texte."""
    with open(file_path, 'r') as file:
        usernames = file.read().splitlines()
    return usernames

async def create_public_channel(username):
    """Crée un canal public avec le nom d'utilisateur donné et définit l'URL du canal."""
    try:
        # Nom du canal
        channel_name = f"{username} Sniper"
        
        # Création du canal public
        result = await client(CreateChannelRequest(
            title=channel_name,
            about='Canal créé automatiquement pour Sniper',
            megagroup=False  # Canal public
        ))

        channel_id = result.chats[0].id  # Récupère l'ID du canal créé
        print(f"✅ Canal public créé : {channel_name}")

        # Attendre un peu avant de définir le nom d'utilisateur
        time.sleep(10)  # Augmenter le temps d'attente pour s'assurer que les changements sont pris en compte

        # Essayer de définir le nom d'utilisateur du canal
        try:
            await client(UpdateUsernameRequest(
                channel=channel_id,
                username=username
            ))
            print(f"✅ Tentative de mise à jour du nom d'utilisateur : @{username}")
            
            # Vérifier si le nom d'utilisateur a été ajouté correctement
            time.sleep(10)  # Attente pour la mise à jour du nom d'utilisateur
            try:
                # Essayer d'obtenir les informations du canal après la mise à jour
                channels = await client(GetChannelsRequest(id=[channel_id]))
                channel = channels.chats[0]
                if channel.username == username:
                    print(f"✅ Nom d'utilisateur confirmé : @{username}")
                    print(f"🌐 URL du canal : https://t.me/{username}")
                else:
                    print(f"❌ Nom d'utilisateur non mis à jour : @{username}")

            except Exception as e:
                print(f"❌ Erreur lors de la vérification du nom d'utilisateur : {e}")

        except UsernameOccupiedError:
            print(f"❌ Nom d'utilisateur @{username} déjà pris.")
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
    """Fonction principale du script."""
    await client.start(PHONE_NUMBER)
    
    # Demande du fichier contenant les noms d'utilisateur à vérifier
    file_path = input("📂 Entrez le chemin du fichier texte contenant les noms d'utilisateur à vérifier : ")
    usernames = get_usernames_from_file(file_path)
    
    while True:
        for username in usernames:
            if username.isalnum():  # Vérifie si le nom d'utilisateur est valide (vous pouvez ajouter d'autres vérifications)
                print(f"✅ Nom d'utilisateur valide : {username}")
                # Création du canal public avec le nom d'utilisateur
                await create_public_channel(username)
                break
            else:
                print(f"❌ Nom d'utilisateur non valide : {username}")
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
