using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FloatingText : MonoBehaviour
{
    [SerializeField] Animation anim;
    [SerializeField] float destroyTime; // 몇 초 후에 텍스트 파괴시킬지

    // Start is called before the first frame update
    void Start()
    {
        anim.Play();
        Destroy(gameObject, destroyTime);
    }
}
