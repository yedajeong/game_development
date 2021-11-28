using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Ending : MonoBehaviour
{
    public GameObject creditAnim;
    public GameObject fadeoutAnim;
    public GameObject hamRunAnim;
    public GameObject hamEatAnim;

    void Start()
    {
        hamRunAnim.SetActive(true);
        hamEatAnim.SetActive(true);
        fadeoutAnim.SetActive(true);
        creditAnim.SetActive(true);
        
    }

    public void ExitBt()
    {
        Application.Quit();
    }

}
