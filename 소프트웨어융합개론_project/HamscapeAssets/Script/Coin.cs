using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Coin : MonoBehaviour
{

    private void OnTriggerEnter(Collider other)
    {
        if (other.tag == "Player")
        {
            SoundManager.instance.PlaySE("coin");
            FloatingTextManager.instance.CreateFloatingText(gameObject.transform.position);
            GameManager gameManager = FindObjectOfType<GameManager>();
            gameManager.CoinCheck();
            Destroy(gameObject);
        }
    }
}
