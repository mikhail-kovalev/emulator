import org.example.ShellEmulator;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class TestEmulator {
    private ShellEmulator emulator;

    @BeforeEach
    void setUp() throws Exception {
        emulator = new ShellEmulator("User", "Fs", "start");
    }

    @Test
    void testDate() {
        emulator.DateLine();
        assertTrue(emulator.getConsole().getText().contains("SEPTEMBER"));
    }
    @Test
    void testCDLS(){
        emulator.executeCommand("cd Papcka1");
        emulator.executeCommand("ls");
        assertTrue(emulator.getConsole().getText().contains("Otchet.docx"));
    }
    @Test
    void testCDLS2(){
        emulator.executeCommand("cd Papcka1");
        emulator.executeCommand("ls");
        emulator.executeCommand("cd ..");
        assertTrue(emulator.getConsole().getText().contains("Otchet.docx"));
    }

    @Test
    void testLSTail(){
        emulator.executeCommand("ls");
        emulator.executeCommand("tail start.sh");
        assertTrue(emulator.getConsole().getText().contains("echo"));
    }
    @Test
    void testLSTail2(){
        emulator.executeCommand("ls");
        try {
            emulator.executeCommand("tail start");
        }
        catch (Exception e) {
        }
    }
    /*
    @Test
    void testExit() {
        assertDoesNotThrow(() -> emulator.executeCommand("exit"));
    }
     */
}
