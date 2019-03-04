%matplotlib inline
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def drew(X_train,Y):
    x_a = X_train[y_train==0,2]
    y_a = X_train[y_train==0,0]
    z_a =X_train[y_train==0,1]
    x_b = X_train[y_train==1,2]
    y_b = X_train[y_train==1,0]
    z_b = X_train[y_train==1,1]
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d')
    p1 = ax.scatter(x_a,y_a,z_a,color='b')
    p2 = ax.scatter(x_b,y_b,z_b,color='r')

    x_p,y_p = np.meshgrid(
                        np.linspace(0 , 4 ,100),
                       np.linspace(0, 300,100)
                      ) 
    W = w[0] 
   
    z_p =( W[2]*x_p+W[0]*y_p+b) /W[1]
    surf = ax.plot_surface(x_p, y_p,z_p, rstride=1, cstride=1,alpha=0.7,color="black")
    
    plt.legend([ p2,p1], ['neg', 'pos'], scatterpoints=1)
    ax.set_xlim((0, 4))
    ax.set_ylim((0,300)) 
    ax.set_zlim((0,40))
    plt.title("sql sample")    #修改
#     plt.gca().invert_xaxis() 
#     plt.show()
    
    plt.savefig("C:/Users/asus/Desktop/test/sql.jpg",dpi=300) #修改
drew(X_train,y_train)
