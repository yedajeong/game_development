using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    private PlayerController thePlayer;
    public GameObject player;
    public int coinNumber = 0;
    private bool isGamefinish = false;

    public Text coinText; //현재 코인갯수를 표시할 텍스트
    public GameObject clearPanel;
    public GameObject gameoverPanel;

    void Start()
    {
        thePlayer = FindObjectOfType<PlayerController>();
        coinNumber = 0;
        isGamefinish = false;
    }

    void Update()
    {
        if (isGamefinish == true && coinNumber == 5 && thePlayer.currentMap == "Bathroom") //게임클리어
        {
            Destroy(player);
            SceneManager.LoadScene("Ending");
            
        }
        else if (isGamefinish == true && coinNumber == 5 ) //스테이지 클리어
        {
            clearPanel.SetActive(true);
        }
        else if (isGamefinish == true && coinNumber != 5)//게임오버
        {
            gameoverPanel.SetActive(true);
        }
    }

    public void CoinCheck()
    {
        coinNumber++;
        coinText.text = "Coin " + coinNumber + "/5";

        if (coinNumber == 5)
        {
            isGamefinish = true;
            SoundManager.instance.PlaySE("game_clear");
        }
    }

    public void GameOver()
    {
        isGamefinish = true;
        SoundManager.instance.PlaySE("game_over");
    }

    public void RestartBut()
    {
        
        if (thePlayer.currentMap == "Bathroom")
        {
            SceneManager.LoadScene("Bathroom");
            thePlayer.transform.position = new Vector3(-1, 1, 13);
            thePlayer.playerRigidbody.constraints = RigidbodyConstraints.None;
            thePlayer.playerRigidbody.constraints = RigidbodyConstraints.FreezeRotation;
        }
        else   
        {
            Destroy(player);
            SceneManager.LoadScene("Room");
            thePlayer.currentMap = "Room";
        }  
    }

    public void NextStageBut()
    {
        SceneManager.LoadScene("Bathroom");
        isGamefinish = false;
        coinNumber = 0;
        thePlayer.currentMap = "Bathroom";
        thePlayer.transform.position = new Vector3(-1, 1, 13);

    }

    public void HomeBut()
    {
        SceneManager.LoadScene("Home");
        Destroy(player);
        thePlayer.currentMap = "Room";
    }
}
