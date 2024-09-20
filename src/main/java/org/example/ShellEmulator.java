package org.example;

import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.time.LocalDateTime;
import java.util.Enumeration;
import java.util.HashSet;
import java.util.Scanner;
import java.util.Set;
import java.util.zip.*;
import javax.swing.*;

public class ShellEmulator extends JFrame implements ActionListener {

    private JTextArea console;
    private JTextField commandLine;
    private String currentDirectory;
    private String ResoursePath="C:\\Users\\nazar\\OneDrive\\Desktop\\FirstConfig\\src\\main\\resources\\";
    private String username;
    private ZipFile vfs;
    private String startScript;


    public JTextArea getConsole() {
        return console;
    }

    public ShellEmulator(String username, String vfsPath, String startScript) throws FileNotFoundException {
        super("Shell Emulator");
        vfsPath=ResoursePath+vfsPath+".zip";
        startScript=ResoursePath+startScript+".sh";
        this.username = username;
        this.currentDirectory = "/";
        this.startScript = startScript;
        try {
            this.vfs = new ZipFile(vfsPath);
        } catch (IOException e) {
            System.err.println("Error open vfs: " + e.getMessage());
            System.exit(1);
        }
        // Создание GUI
        JPanel contentPane = new JPanel(new BorderLayout());
        console = new JTextArea();
        console.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(console);
        contentPane.add(scrollPane, BorderLayout.CENTER);

        commandLine = new JTextField();
        commandLine.addActionListener(this);
        contentPane.add(commandLine, BorderLayout.SOUTH);

        add(contentPane);
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setVisible(true);

        // Выполнение стартового скрипта
        if (startScript != null) {
            executeScript(startScript);
        }

        printPrompt();
    }

    @Override
    public void actionPerformed(ActionEvent e) {
        String command = commandLine.getText();
        commandLine.setText("");
        console.append(username + "@" + currentDirectory + "$ " + command + "\n");

        if (command.equalsIgnoreCase("exit")) {
            System.exit(0);
        } else {
            executeCommand(command);
        }

        printPrompt();
    }

    public void executeCommand(String command) {
        String[] parts = command.split(" ");
        String cmd = parts[0];
        switch (cmd) {
            case "ls":
                showList(listDirectory());
                break;
            case "cd":
                if (parts.length > 1) {
                    changeDirectory(parts[1]);
                }
                break;
            case "echo":
                console.append(command.split(" ")[1] + "\n");
                break;
            case "date":
                DateLine();
                break;
            case "tail":
                TailExecuter(command.split(" ")[1]);
                break;
            case "exit":
                System.exit(0);
                break;
            default:
                console.append("Unknown Command: " + cmd + "\n");
                break;
        }
    }

    public void DateLine(){
        LocalDateTime time = LocalDateTime.now();
        String timeToConsole = time.getDayOfWeek()+ " "+time.getMonth()+" "+time.getDayOfMonth()+" ";
        timeToConsole+= time.getHour()+" "+time.getMinute()+" "+time.getSecond();
        console.append(timeToConsole+ "\n");

    }

    public void TailExecuter(String path){
        if (!path.contains(".")){
            throw new RuntimeException();
        }
        String oldCurrent = currentDirectory;
        if(path.replace(currentDirectory.substring(1),"").contains("/")){
            currentDirectory=path.substring(0,path.lastIndexOf("/"));
        }
        ZipEntry fileFinded=getFile(path.substring(path.lastIndexOf("/")!=-1 ?
                path.lastIndexOf("/") : 0, path.length()));
        BufferedReader br = null;
        try {
            br = new BufferedReader(new InputStreamReader(vfs.getInputStream(fileFinded)));
            String line;
            while (true) {
                try {
                    if (!((line = br.readLine()) != null)) break;
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
                console.append(line + "\n");
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        currentDirectory=oldCurrent;
    }

    private void executeScript(String script) throws FileNotFoundException {
        FileReader fr = new FileReader(new File(script));
        Scanner sc = new Scanner(fr);
        while (sc.hasNextLine()) {
            String line=sc.nextLine();
            console.append(username + "@" + currentDirectory + "$ " + line + "\n");
            executeCommand(line);
        }
    }

    private Set<String> listDirectory() {
        Enumeration<? extends ZipEntry> entries = vfs.entries();
        Set<String> files = new HashSet<>();
        while(entries.hasMoreElements()){
            ZipEntry entry = entries.nextElement();
            if(currentDirectory.equals("/")){
                files.add(entry.getName().split("/")[0]);
            }else if(entry.getName().contains(currentDirectory.substring(1)) && !currentDirectory.equals("/")){
                String file = entry.getName().replace(currentDirectory.substring(1),"");
                files.add(file.split("/")[0]);
            }
        }
        return files;
    }

    public ZipEntry getFile(String name) {
        Enumeration<? extends ZipEntry> entries = vfs.entries();
        while(entries.hasMoreElements()){
            ZipEntry entry = entries.nextElement();
            if(currentDirectory.equals("/") && entry.getName().contains(name) ){
                return entry;
            }else if(entry.getName().contains(currentDirectory.substring(1)) && !currentDirectory.equals("/")){
                String file = entry.getName().replace(currentDirectory.substring(1),"");
                if(file.contains(name)){
                    return entry;
                }
            }
        }
        return null;
    }
    private void showList(Set<String> files){
        for (String file : files) {
            console.append(file+"\n");
        }
    }
    private boolean findIn(Set<String> files,String name){
        for (String file : files) {
            if(file.contains(name)){
                return true;
            }
        }
        return false;
    }

    private void changeDirectory(String dir) {
        System.out.println(dir);
        System.out.println(currentDirectory);
        if (dir.equals("..") && !currentDirectory.equals("/")) {
            currentDirectory = currentDirectory.substring(0, currentDirectory.lastIndexOf("/"));
            currentDirectory = currentDirectory.substring(0, currentDirectory.lastIndexOf("/"));
            if (currentDirectory.isEmpty()) {
                currentDirectory = "/";
            }
            System.out.println(currentDirectory);
        } else {
            if(findIn(listDirectory(),dir)){
                currentDirectory = currentDirectory  + dir+"/";
            }else{
                console.append("error wrong path\n");
            }
        }
    }

    private void printPrompt() {
        console.append(username + "@" + currentDirectory + "$ ");
    }
    public static void main(String[] args) throws FileNotFoundException {
        // Запуск эмулятора с параметрами командной строки
        if (args.length != 3) {
            System.err.println("Использование: ShellEmulator <имя_пользователя> <vfs_путь> <скрипт_путь>");
            System.exit(1);
        }

        new ShellEmulator(args[0], args[1], args[2]);
    }
}
