using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class torchere : MonoBehaviour
{
    [SerializeField]
    private GameObject torchLight;

    void OnTriggerEnter(Collider other)
    {
        if (other.tag == "Player")
        {
            torchLight.SetActive(true);
        }
    }
}
