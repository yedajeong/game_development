using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/*[System.Serializable]
public class Sound
{
    public string soundName;
    public AudioClip clip;
}*/

public class IntroEndingSound : MonoBehaviour
{
    public static IntroEndingSound instance;

    [Header("사운드 등록")]
    [SerializeField] Sound bgmSounds;

    [Header("브금플레이어")]
    [SerializeField] AudioSource bgmPlayer;

    void Start()
    {
        instance = this;
        bgmPlayer.clip = bgmSounds.clip;
        bgmPlayer.Play();
    }
}

