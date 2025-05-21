import requests

def fetch_free_models():
    url = "https://openrouter.ai/api/v1/models"
    response = requests.get(url)
    # # save response to file
    # with open("openrouter_models.json", "w") as file:
    #     file.write(response.text)
    if response.status_code == 200:
        models = response.json()["data"]
        free_models = [model for model in models if model["pricing"]["prompt"] == "0" and model["pricing"]["completion"] == "0"]
        # Trier par 'top_provider.context_length' décroissant
        free_models = sorted(free_models, key=lambda model: model["top_provider"]["context_length"], reverse=True)
        return free_models
    else:
        print("Erreur :", response.status_code)
        return []

def get_free_model_ids():
    free_models = fetch_free_models()
    return [model["id"] for model in free_models]

def print_free_model_ids_and_names():
    free_models = fetch_free_models()
    for model in free_models:
        context_length = model["top_provider"]["context_length"]
        print(f"ID: {model['id']}, Name: {model['name']}, Context Length: {context_length}")

def save_free_model_ids_to_file():
    free_models = fetch_free_models()
    with open("openrouter_free_id_list.txt", "w") as file:
        for model in free_models:
            file.write(f"{model['id']}\n")
    print("fichier openrouter_free_id_list.txt mis à jour")

if __name__ == "__main__":
    # Test de chaque fonction
    print("Liste des IDs des modèles gratuits :")
    print(get_free_model_ids())
    
    print("\nListe des IDs, noms et context length des modèles gratuits :")
    print_free_model_ids_and_names()
    
    print("\nSauvegarde des IDs des modèles gratuits dans un fichier :")
    save_free_model_ids_to_file()