using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ToiletCover : MonoBehaviour
{
    private Animator animator;
    private bool toiletOpen;
    // Start is called before the first frame update
    void Start()
    {
        toiletOpen = false;
        animator = GetComponent<Animator>();
    }

    private void OnTriggerStay(Collider other)
    {
        if (other.tag == "Player")
        {
            toiletOpen = true;
            Cover("Open");
            Debug.Log("stay");
        }
    }

    private void Cover(string direction)
    {
        animator.SetTrigger(direction);
    }
}
