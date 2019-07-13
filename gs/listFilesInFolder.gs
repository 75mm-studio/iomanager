function listFilesInFolder(folderName) {

   var sheet = SpreadsheetApp.getActiveSheet();
   sheet.appendRow(["Name", "Date", "Size", "URL", "Download", "Description", "Image"]);


//change the folder ID below to reflect your folder's ID (look in the URL when you're in your folder)
    var folder = DriveApp.getFolderById("1VtUkxTwylUQ1xxVgnjIifYlp6Fytnbv2");
    var contents = folder.getFiles();

    var cnt = 0;
    var file;

    while (contents.hasNext()) {
        var file = contents.next();
        cnt++;

           data = [
                file.getName(),
                file.getDateCreated(),
                file.getSize(),
                file.getUrl(),
                "https://docs.google.com/uc?export=download&confirm=no_antivirus&id=" + file.getId(),
                file.getDescription(),
                "=image(\"https://docs.google.com/uc?export=download&id=" + file.getId() + '"' + ",2" + ")",
            ];

            sheet.appendRow(data);



    };
};
