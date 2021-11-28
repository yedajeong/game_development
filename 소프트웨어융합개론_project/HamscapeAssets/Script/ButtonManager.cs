using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class ButtonManager : MonoBehaviour
{
    private PlayerController theplayer;

    public void RestartBut()
    {
        SceneManager.LoadScene("Room");
    }

    public void NextStageBut()
    {
        SceneManager.LoadScene("Bathroom");


    }

    public void HomeBut()
    {
        SceneManager.LoadScene("Home");
    }
}
