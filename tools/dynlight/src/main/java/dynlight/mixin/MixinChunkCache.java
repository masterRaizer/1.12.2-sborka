package dynlight.mixin;

import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import dynlight.LightSources;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.ChunkCache;
import net.minecraft.world.World;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;

/** Terrain (chunk section meshes) is built from a ChunkCache on the chunk builder threads. */
@Mixin(ChunkCache.class)
public abstract class MixinChunkCache {

    @Shadow protected World world;

    @ModifyReturnValue(method = "getCombinedLight", at = @At("RETURN"))
    private int dynlight$addDynamicLight(int packed, BlockPos pos) {
        World w = this.world;
        return w != null && w.isRemote ? LightSources.apply(packed, pos) : packed;
    }
}
