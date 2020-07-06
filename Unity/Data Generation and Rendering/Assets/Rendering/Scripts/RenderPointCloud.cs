using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// This script is responsible for ingesting the neural network (NN) output, a video.
/// Since the NN animates on a precise frame by frame basis, everything is controlled 
/// step by step via a coroutine. Otherwise the animation will not sync up with the 
/// music when we recombine the two via FFMPEG.
/// For each frame in the video it:
/// 1. Reads the frame
/// 2. Determines how many points need to be rendered, and their 3D positions
/// 3. Creates new cubes if needed, or just repositions cubes that have been spawned
/// 4. Calculates the centroid of the figure and sends it to the camera
/// 5. Tells the camera to save an image.
/// </summary>

public class RenderPointCloud : MonoBehaviour
{

    //private variables accessible in the editor


    //variables for ingesting the depth video
    [SerializeField]
    private int forLoopInterval = 3;

    [SerializeField]
    private int frameRate = 1;

    [SerializeField]
    private float whiteValueCuttOff = .1f;

    [SerializeField]
    private float scaleModifier = .02f;

    [SerializeField]
    private float depthMod = 2f;

    [SerializeField]
    private Material cubeMaterial;

    [SerializeField]
    private RenderTexture renderTexture;

    [SerializeField]
    FollowPointCloudCamera userCameraScript;

    [SerializeField]
    RenderImages imageSaveScript;


    //private variables not accessible in the editor


    //variables for reading the depth video
    private UnityEngine.Video.VideoPlayer player;

    [Header("Rendering Progress")]
    public int textureIndex = 1;

    private int totalFrameCount = 100;
    
    private Texture2D newTexture;

    private BoxCollider collider;

    private int numbPointsToRender = 0;

    private float positionScale;

    private float positionModifier;

    private GameObject localCentroidReference;


    //variables for point cloud object pooling
    private List<Vector3> cubePositions = new List<Vector3>();

    private List<float> pixelValues = new List<float>();

    private List<GameObject> allCubes = new List<GameObject>();

    private List<Vector3> allCubesVelocities = new List<Vector3>();

    private Vector3 newPointCacheVariable = Vector3.zero;


    
    //variables for calculating the centroid or center of mass of the point cloud
    private float totalXValue = 0;

    private float totalYValue = 0;

    private float totalZValue = 0;

    private Vector3 centroid = Vector3.zero;
    

    void Awake(){

        collider = GetComponent<BoxCollider>();

        //texture for reading the video
        newTexture = new Texture2D(128, 128, TextureFormat.RGB24, true);

        //position modifiers based of image size and plane collider size.
        positionScale = (collider.size.x/newTexture.width) * transform.localScale.x;
        positionModifier = (collider.size.x);

        player = GetComponent<UnityEngine.Video.VideoPlayer>();

        player.Prepare();

        player.prepareCompleted += StartVideoLoop;
    }

    void StartVideoLoop(UnityEngine.Video.VideoPlayer vp){

        totalFrameCount = (int) player.frameCount;
        imageSaveScript.allBytesArrays = new byte[totalFrameCount+1][];
        Debug.Log(totalFrameCount);

        localCentroidReference = GameObject.CreatePrimitive(PrimitiveType.Quad);
        localCentroidReference.GetComponent<MeshRenderer>().enabled = false;
        localCentroidReference.transform.parent = transform;

        StartCoroutine("GenerateGeometry");

    }

    IEnumerator GenerateGeometry(){

        if(textureIndex>totalFrameCount){
            StopSequence();
        }

        //reset all values from last frame
        for(int i = 0; i<allCubes.Count; i++){
            allCubes[i].SetActive(false);
        }

        cubePositions.Clear();
        pixelValues.Clear();

        //xyz values for centroid
        totalXValue = 0;
        totalYValue = 0;
        totalZValue = 0;

        //get next frame of video
        player.frame = textureIndex;
        player.Play();


        if(renderTexture == null){
            yield return null;
        }

        RenderTexture.active = renderTexture;
        newTexture.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        newTexture.Apply();

        // loop through video frame and position points based off of depth info, then add of position values for depth data to figure out centroid later
        for(int x = 0; x<newTexture.width; x+=forLoopInterval){
            for(int y = 0; y<newTexture.width; y+=forLoopInterval){
            
                Color pixelColor = newTexture.GetPixel(x, y);

                float value = 1-pixelColor.r;

                if (value > whiteValueCuttOff){

                    newPointCacheVariable.x = (x*positionScale)-positionModifier;
                    newPointCacheVariable.y = (y*positionScale)-positionModifier/2f;
                    newPointCacheVariable.z = transform.position.z+(value*depthMod);

                    cubePositions.Add(newPointCacheVariable);

                    pixelValues.Add(value);

                    totalXValue += newPointCacheVariable.x;
                    totalYValue += newPointCacheVariable.y;
                    totalZValue += transform.position.z+(value*depthMod);

                }
            }
        }

        //figure out how many new cubes we want to generate, we don't want to generate new cubes if we don't have to.
        int numberOfPointsToGenerate = cubePositions.Count - numbPointsToRender;

        //reset the number of total generate cubes
        if(numberOfPointsToGenerate > 0){

            numbPointsToRender = cubePositions.Count;

        } 

        //generate the new cubes if we have to
        for(int i = 0; i<numberOfPointsToGenerate; i ++){

            GameObject newCube = GameObject.CreatePrimitive(PrimitiveType.Cube);
            newCube.transform.parent = transform;
            newCube.GetComponent<Renderer>().material = cubeMaterial;
            allCubes.Add(newCube);
            allCubesVelocities.Add(Vector3.zero);
            
        }
    

        //now apply the positional values to all our generate cubes
        for(int i = 0; i<cubePositions.Count; i ++){
            
            float scale = scaleModifier * pixelValues[i];
            allCubes[i].GetComponent<Renderer>().material = cubeMaterial;
            allCubes[i].SetActive(true);
            allCubes[i].transform.localScale = new Vector3(scale,scale,scale);
            allCubes[i].transform.rotation = transform.rotation;
            allCubes[i].transform.localPosition = cubePositions[i];

        }

        //determine centroid value for FollowPointCLoudCamera script

        if(cubePositions.Count>0){

            centroid.x = totalXValue/cubePositions.Count;
            centroid.y = totalYValue/cubePositions.Count;
            centroid.z = totalZValue/cubePositions.Count;

            localCentroidReference.transform.localPosition = centroid;
    
            //send FollowPointCLoudCamera script centroid and local look at reference
            userCameraScript.UpdateCameraPosition(centroid,localCentroidReference.transform.position);

        }
        
        
        if(imageSaveScript.takePhotos){

            imageSaveScript.StoreImage();
            
        }

        textureIndex+=frameRate;


        yield return null;

        //run the loop again
        StartCoroutine("GenerateGeometry");


    }

    void StopSequence(){
        if(imageSaveScript.takePhotos){
            imageSaveScript.SaveAllImages();
        }
        Debug.Log(Time.realtimeSinceStartup);

        #if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
        #endif

        #if UNITY_STANDALONE_OSX
            Application.Quit();
        #endif
        
    }

    
}
