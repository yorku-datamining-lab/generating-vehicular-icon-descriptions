from model import Dataset

# Manual titles
mopar = [
    "2024 Chrysler Pacifica - symbol glossary",
	"2024 Dodge Hornet - symbol glossary",
	"2024 Jeep Grand Cherokee - symbol glossary",
    "2024 Fiat 500e - symbol glossary"
]
volvo = [
    'XC40 Recharge Pure Electric Indicator and warning symbols _ Volvo Support EN-CA',
    'C40 Recharge Indicator and warning symbols _ Volvo Support EN-CA',
    'EC40 Indicator and warning symbols _ Volvo Support EN-CA',
    'EX40 Indicator and warning symbols _ Volvo Support EN-CA',
    'S60 Indicator and warning symbols _ Volvo Support EN-CA',
    'S60 Recharge Plug-in Hybrid Indicator and warning symbols _ Volvo Support EN-CA',
    'S90 Indicator and warning symbols _ Volvo Support EN-CA',
    'S90 Recharge Plug-in Hybrid Indicator and warning symbols _ Volvo Support EN-CA',
    'V60 Indicator and warning symbols _ Volvo Support EN-CA',
    'V60 Plug-in Hybrid Indicator and warning symbols _ Volvo Support EN-CA',
    'V60 Recharge Plug-in Hybrid Indicator and warning symbols _ Volvo Support EN-CA',
    'V90 Indicator and warning symbols _ Volvo Support EN-CA',
    'XC40 Recharge Plug-in Hybrid Indicator and warning symbols _ Volvo Support EN-CA',
    'XC90 Indicator and warning symbols _ Volvo Support EN-CA',
    'XC90 Recharge Plug-in Hybrid Indicator and warning symbols _ Volvo Support EN-CA'
]
jlr = [
    'Land Rover 2019 Range Rover Evoque',
    'Land Rover 2024 Discovery Sport',
    'Land Rover 2022 Range Rover',
    'Land Rover 2024 New Range Rover Evoque',
    'Land Rover 2022 Range Rover Sport',
    'Land Rover 2024 New Range Rover', 
    'Land Rover 2024 Defender', 
    'Land Rover 2024 New Range Rover Sport', 
    'Land Rover 2024 Discovery',
    'Land Rover 2024 Range Rover Velar',
    'Jaguar 2018 F-Type',
    'Jaguar 2018 XJ',
    'Jaguar 2024 F-PACE',
    'Jaguar 2018 XE',
    'Jaguar 2024 E-PACE',
    'Jaguar 2024 XF'
]
mazda = [
    "2024 Mazda CX-50 Owner's Manual _ Mazda Canada", 
    "2023 MX-30 Owner's Manual _ Mazda Canada",
    "2024 Mazda MX-5 Owner's Manual _ Mazda USA",
    "2024 Mazda3 Owner's Manual _ Mazda Canada",
    "2025 Mazda CX-70 Owner's Manual _ Mazda Canada",
    "2024 Mazda CX-30 Owner's Manual _ Mazda Canada",
    "2024 Mazda CX-90 Owner's Manual _ Mazda Canada",
]
mazda_icon_blacklist = [
    # Webpage icons
    "70b2694dd4862b45",
    "072b96d44c69b270",
    # Not icons
    "71ccb25a732bb6b6",
    "71d4949636229c94",
    "238c136969695571",
    "238c176369694571",
    # Multiple icons
    "d4da9b9ad89ada94",
    "d4c4d4d416969696",
    "d4c4d4d4d4d4d4d4",
    "d4d4d4d4d4961696",
    "9595959595919595",
    "5484c4d417969696",
    "4941c96d4b4bc149", 
    "0101159515350101",
    "49c1c9e9cb4b4149",
    "0101959595950101"
]

def main():
    # New empty dataset
    dataset = Dataset("All Manuals - Ground Truth Only")
    data_folder = "data/manuals"
    
    # Load manuals
    for m in mopar:
        dataset.load_manual(
            manual_name="Mopar",
            html_file=f"{data_folder}/mopar/{m}.html",
            img_folder=f"{data_folder}/mopar/{m}_files",    
            root_tag_attr = {"id":"manual-details"},
            ascend = 2
        )

    for m in volvo:
        dataset.load_manual(
            manual_name="Volvo",
            html_file=f"{data_folder}/volvo/{m}.html",
            img_folder=f"{data_folder}/volvo/{m}_files",    
            root_tag_name="article",
            ascend=4
        )
    dataset.load_manual(
        manual_name="Volvo",
        html_file=f"{data_folder}/volvo/EX30 Warning and indicator symbols _ Volvo Support EN-CA.html",
        img_folder=f"{data_folder}/volvo/EX30 Warning and indicator symbols _ Volvo Support EN-CA_files",    
        root_tag_name="article",
        ascend=2
    )

    for m in jlr:
        dataset.load_manual(
            manual_name="JLR",
            html_file=f"{data_folder}/jlr/{m}.html",
            img_folder=f"{data_folder}/jlr/{m}_files",
            root_tag_name="body",
            ascend=2
        )

    for m in mazda:
        dataset.load_manual(
            manual_name="Mazda",
            html_file=f"{data_folder}/mazda/{m}.html",
            img_folder=f"{data_folder}/mazda/{m}_files",
            root_tag_attr = {"id":"main"},
            ascend = 3
        )
    
    # Delete some blacklisted Mazda icons
    for dhash in mazda_icon_blacklist:
        try:
            dataset.delete_icon(dhash)
        except KeyError:
            print(dhash)

    # Load ground truth descriptions
    dataset.load_json("data/groundtruth/groundtruth.json")

    # Save dataset
    dataset.save_json("data/groundtruth/groundtruth.json")

    print(len(dataset.icons))

if __name__ == "__main__":
    main()