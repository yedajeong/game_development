using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class Home : MonoBehaviour
{
    [SerializeField]
    private GameObject manual;

    public void StartBut()
    {
        SceneManager.LoadScene("Room");
    }

    public void ExitBut()
    {
        Application.Quit();
    }

    public void ManualBut()
    {
        manual.SetActive(true);
    }

    public void ManualExitBut()
    {
        manual.SetActive(false);
    }
}
